# Rekall Memory Forensics
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Authors:
# Michael Cohen <scudette@users.sourceforge.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

""" This plugin contains CORE classes used by lots of other plugins """

# pylint: disable=protected-access

import logging
import re

from rekall import args
from rekall import scan
from rekall import obj
from rekall import plugin
from rekall import utils

from rekall.plugins import core


# We require both a physical AS set and a valid profile for
# AbstractWindowsCommandPlugins.

class AbstractWindowsCommandPlugin(plugin.PhysicalASMixin,
                                   plugin.ProfileCommand):
    """A base class for all windows based plugins.

    Windows based plugins require at a minimum a working profile, and a valid
    physical address space.
    """

    __abstract = True

    @classmethod
    def is_active(cls, config):
        """We are only active if the profile is windows."""
        return (getattr(config.profile, "_md_os", None) == 'windows' and
                plugin.Command.is_active(config))


class WinFindDTB(AbstractWindowsCommandPlugin):
    """A plugin to search for the Directory Table Base for windows systems.

    There are a number of ways to find the DTB:

    - Scanner method: Scans the image for a known kernel process, and read the
      DTB from its Process Environment Block (PEB).

    - Get the DTB from the KPCR structure.

    - Note that the kernel is mapped into every process's address space (with
      the exception of session space which might be different) so using any
      process's DTB from the same session will work to read kernel data
      structures. If this plugin fails, try psscan to find potential DTBs.
    """

    __name = "find_dtb"

    # We scan this many bytes at once
    SCAN_BLOCKSIZE = 1024 * 1024

    @classmethod
    def args(cls, parser):
        """Declare the command line args we need."""
        super(WinFindDTB, cls).args(parser)
        parser.add_argument("--process_name",
                            help="The name of the process to search for.")

    def __init__(self, process_name=None, **kwargs):
        """Scans the image for the Idle process.

        Args:
          process_name: The name of the process we should look for. (If we are
            looking for the kernel DTB, any kernel process will do here.)

          physical_address_space: The address space to search. If None, we use
            the session's physical_address_space.

          profile: An optional profile to use (or we use the session's).
        """
        super(WinFindDTB, self).__init__(**kwargs)

        self.process_name = process_name or "Idle"

        # This is the offset from the ImageFileName member to the start of the
        # _EPROCESS
        self.image_name_offset = self.profile.get_obj_offset(
            "_EPROCESS", "ImageFileName")

    def scan_for_process(self):
        """Scan the image for the idle process."""
        needle = self.process_name + "\x00" * (15 - len(self.process_name))
        offset = 0
        while self.physical_address_space.is_valid_address(offset):
            data = self.physical_address_space.read(offset, self.SCAN_BLOCKSIZE)
            found = 0

            while 1:
                found = data.find(needle, found + 1)
                if found >= 0:
                    # We found something that looks like the process we want.
                    self.eprocess = self.profile.Object(
                        "_EPROCESS",
                        offset=offset + found - self.image_name_offset,
                        vm=self.physical_address_space)

                    yield self.eprocess
                else:
                    break

            offset += len(data)

    def dtb_hits(self):
        for eprocess in self.scan_for_process():
            result = eprocess.Pcb.DirectoryTableBase.v()
            if result:
                yield result, eprocess

    def verify_address_space(self, eprocess, address_space):
        """Check the eprocess for sanity."""
        # In windows the DTB must be page aligned, except for PAE images where
        # its aligned to a 0x20 size.
        if not self.profile.metadata("pae") and address_space.dtb & 0xFFF != 0:
            return False

        if self.profile.metadata("pae") and address_space.dtb & 0xF != 0:
            return False

        version = self.profile.metadata("major"), self.profile.metadata("minor")
        # The test below does not work on windows 8 with the idle process.
        if version < (6, 2):
            # Reflect through the address space at ourselves. Note that the Idle
            # process is not usually in the PsActiveProcessHead list, so we use
            # the ThreadListHead instead.
            list_head = eprocess.ThreadListHead.Flink

            if list_head == 0:
                return False

            me = list_head.dereference(vm=address_space).Blink.Flink
            if me.v() != list_head.v():
                return False

        return True

    def render(self, renderer):
        renderer.table_header(
            [("_EPROCESS (P)", "physical_eprocess", "[addrpad]"),
             ("DTB", "dtv", "[addrpad]"),
             ("Valid", "valid", "")])

        for dtb, eprocess in self.dtb_hits():
            address_space = core.GetAddressSpaceImplementation(self.profile)(
                session=self.session, base=self.physical_address_space, dtb=dtb)

            renderer.table_row(
                eprocess.obj_offset, dtb,
                self.verify_address_space(eprocess, address_space))


## The following are checks for pool scanners.

class PoolTagCheck(scan.ScannerCheck):
    """ This scanner checks for the occurance of a pool tag """
    def __init__(self, tag=None, tags=None, **kwargs):
        super(PoolTagCheck, self).__init__(**kwargs)
        self.tags = tags or [tag]

        # The offset from the start of _POOL_HEADER to the tag.
        self.tag_offset = self.profile.get_obj_offset(
            "_POOL_HEADER", "PoolTag")

    def skip(self, data, offset, **_):
        nextvals = []
        for tag in self.tags:
            nextval = data.find(tag, offset + 1)
            if nextval >= 0:
                nextvals.append(nextval)

        # No tag was found
        if not nextvals:
            # Substrings are not found - skip to the end of this data buffer
            return len(data) - offset + 1

        return min(nextvals) - offset - self.tag_offset

    def check(self, offset):
        for tag in self.tags:
            # Check the tag field.
            data = self.address_space.read(offset + self.tag_offset, len(tag))
            if data == tag:
                return True


class CheckPoolSize(scan.ScannerCheck):
    """ Check pool block size """
    def __init__(self, condition=None, min_size=None, **kwargs):
        super(CheckPoolSize, self).__init__(**kwargs)
        self.condition = condition
        if min_size:
            self.condition = lambda x: x >= min_size

        self.pool_align = self.profile.constants['PoolAlignment']

    def check(self, offset):
        pool_hdr = self.profile._POOL_HEADER(
            vm=self.address_space, offset=offset)

        block_size = pool_hdr.BlockSize.v()

        return self.condition(block_size * self.pool_align)


class CheckPoolType(scan.ScannerCheck):
    """ Check the pool type """
    def __init__(self, paged=False, non_paged=False, free=False, **kwargs):
        super(CheckPoolType, self).__init__(**kwargs)
        self.non_paged = non_paged
        self.paged = paged
        self.free = free

    def check(self, offset):
        pool_hdr = self.profile._POOL_HEADER(
            vm=self.address_space, offset=offset)

        return ((self.non_paged and pool_hdr.NonPagedPool) or
                (self.free and pool_hdr.FreePool) or
                (self.paged and pool_hdr.PagedPool))


class CheckPoolIndex(scan.ScannerCheck):
    """ Checks the pool index """
    def __init__(self, value=0, **kwargs):
        super(CheckPoolIndex, self).__init__(**kwargs)
        self.value = value

    def check(self, offset):
        pool_hdr = self.profile._POOL_HEADER(
            vm=self.address_space, offset=offset)

        return pool_hdr.PoolIndex == self.value


class PoolScanner(scan.DiscontigScanner, scan.BaseScanner):
    """A scanner for pool allocations."""

    # These objects are allocated in the pool allocation.
    allocation = ['_POOL_HEADER']

    def scan(self, offset=0, maxlen=None):
        """Yields instances of _POOL_HEADER which potentially match."""

        maxlen = maxlen or self.profile.get_constant("MaxPointer")
        for hit in super(PoolScanner, self).scan(offset=offset, maxlen=maxlen):
            yield self.profile._POOL_HEADER(vm=self.address_space, offset=hit)


class PoolScannerPlugin(plugin.KernelASMixin, AbstractWindowsCommandPlugin):
    """A base class for all pool scanner plugins."""
    __abstract = True

    @classmethod
    def args(cls, parser):
        super(PoolScannerPlugin, cls).args(parser)
        parser.add_argument(
            "--scan_in_kernel", default=False, action="store_true",
            help="Scan in the kernel address space")

    def __init__(self, address_space=None, scan_in_kernel=False, **kwargs):
        """Scan the address space for pool allocations.

        Args:
          address_space: If provided we scan this address space, else we use the
          physical_address_space.

          scan_in_kernel: Scan in the kernel address space.
        """
        super(PoolScannerPlugin, self).__init__(**kwargs)
        scan_in_kernel = scan_in_kernel or self.session.scan_in_kernel
        if scan_in_kernel:
            self.address_space = address_space or self.kernel_address_space
        else:
            self.address_space = address_space or self.physical_address_space


class KDBGMixin(plugin.KernelASMixin):
    """A plugin mixin to make sure the kdbg is set correctly."""

    @classmethod
    def args(cls, parser):
        """Declare the command line args we need."""
        super(KDBGMixin, cls).args(parser)
        parser.add_argument("--kdbg", action=args.IntParser,
                            help="Location of the KDBG structure.")

    def __init__(self, kdbg=None, **kwargs):
        """Ensure there is a valid KDBG object.

        Args:
          kdbg: The location of the kernel debugger block (In the physical
             AS).
        """
        super(KDBGMixin, self).__init__(**kwargs)
        self.kdbg = kdbg or self.session.GetParameter("kdbg")

        # If the user specified the kdbg use it - even if it looks wrong!
        if self.kdbg and not isinstance(self.kdbg, obj.BaseObject):
            kdbg = self.profile._KDDEBUGGER_DATA64(
                offset=int(self.kdbg), vm=self.kernel_address_space)

            # If the user specified the kdbg use it - even if it looks wrong!
            # This allows the user to force a corrupt kdbg.
            self.kdbg = kdbg

        if self.kdbg is None:
            logging.info(
                "KDBG not provided - Rekall Memory Forensics will try to "
                "automatically scan for it now using plugin.kdbgscan.")

            for kdbg in self.session.plugins.kdbgscan(
                session=self.session).hits():
                # Just return the first one
                logging.info("Found a KDBG hit %r. Hope it works. If not try "
                             "setting it manually.", kdbg)

                # Cache this for next time in the session.
                self.kdbg = kdbg
                self.session.StoreParameter("kdbg", int(kdbg))
                break

        # Allow kdbg to be an actual object.
        if isinstance(self.kdbg, obj.BaseObject):
            return

        # Or maybe its an integer representing the offset.
        elif self.kdbg:
            self.kdbg = self.profile._KDDEBUGGER_DATA64(
                offset=int(self.kdbg), vm=self.kernel_address_space)
        else:
            self.kdbg = obj.NoneObject("Could not guess kdbg offset")


class WindowsCommandPlugin(KDBGMixin, AbstractWindowsCommandPlugin):
    """A windows plugin which requires the kernel address space."""
    __abstract = True


class WinProcessFilter(KDBGMixin, AbstractWindowsCommandPlugin):
    """A class for filtering processes."""

    __abstract = True

    @classmethod
    def args(cls, parser):
        """Declare the command line args we need."""
        super(WinProcessFilter, cls).args(parser)

        parser.add_argument("--eprocess", action=args.ArrayIntParser, nargs="+",
                            help="Kernel addresses of eprocess structs.")

        parser.add_argument("--phys_eprocess",
                            action=args.ArrayIntParser, nargs="+",
                            help="Physical addresses of eprocess structs.")

        parser.add_argument("--pid",
                            action=args.ArrayIntParser, nargs="+",
                            help="One or more pids of processes to select.")

        parser.add_argument("--proc_regex", default=None,
                            help="A regex to select a process by name.")

        parser.add_argument("--eprocess_head", action=args.IntParser,
                            help="Use this as the process head. If "
                            "specified we do not use kdbg.")

    def __init__(self, eprocess=None, phys_eprocess=None, pid=None,
                 proc_regex=None, eprocess_head=None, **kwargs):
        """Filters processes by parameters.

        Args:
           physical_eprocess: One or more EPROCESS structs or offsets defined in
              the physical AS.

           pid: A single pid.

           proc_regex: A regular expression for filtering process name (using
             _EPROCESS.ImageFileName).

           eprocess_head: Use this as the start of the process listing (in case
             PsActiveProcessHead is missing).
        """
        super(WinProcessFilter, self).__init__(**kwargs)

        if isinstance(phys_eprocess, (int, long)):
            phys_eprocess = [phys_eprocess]
        elif phys_eprocess is None:
            phys_eprocess = []

        if isinstance(eprocess, (int, long)):
            eprocess = [eprocess]
        elif isinstance(eprocess, obj.Struct):
            eprocess = [eprocess.obj_offset]
        elif eprocess is None:
            eprocess = []

        self.phys_eprocess = phys_eprocess
        self.eprocess = eprocess

        pids = []
        if isinstance(pid, list):
            pids.extend(pid)

        elif isinstance(pid, (int, long)):
            pids.append(pid)

        if self.session.pid and not pid:
            pids.append(self.session.pid)

        self.pids = pids
        self.proc_regex_text = proc_regex
        if isinstance(proc_regex, basestring):
            proc_regex = re.compile(proc_regex, re.I)

        self.proc_regex = proc_regex
        self.eprocess_head = eprocess_head

        # Sometimes its important to know if any filtering is specified at all.
        self.filtering_requested = (self.pids or self.proc_regex or
                                    self.phys_eprocess or self.eprocess)

    def filter_processes(self):
        """Filters eprocess list using phys_eprocess and pids lists."""
        # No filtering required:
        if not self.filtering_requested:
            for eprocess in self.session.plugins.pslist(
                session=self.session, kdbg=self.kdbg,
                eprocess_head=self.eprocess_head).list_eprocess():
                yield eprocess
        else:
            # We need to filter by phys_eprocess
            for offset in self.phys_eprocess:
                yield self.virtual_process_from_physical_offset(offset)

            for offset in self.eprocess:
                yield self.profile._EPROCESS(vm=self.kernel_address_space,
                                             offset=int(offset))

            # We need to filter by pids
            for eprocess in self.session.plugins.pslist(
                session=self.session, kdbg=self.kdbg,
                eprocess_head=self.eprocess_head).list_eprocess():
                if int(eprocess.UniqueProcessId) in self.pids:
                    yield eprocess
                elif self.proc_regex and self.proc_regex.match(
                    utils.SmartUnicode(eprocess.ImageFileName)):
                    yield eprocess


    def virtual_process_from_physical_offset(self, physical_offset):
        """Tries to return an eprocess in virtual space from a physical offset.

        We do this by reflecting off the list elements.

        Args:
           physical_offset: The physcial offset of the process.

        Returns:
           an _EPROCESS object or a NoneObject on failure.
        """
        physical_eprocess = self.profile._EPROCESS(
            offset=int(physical_offset),
            vm=self.kernel_address_space.base)

        # We cast our list entry in the kernel AS by following Flink into the
        # kernel AS and then the Blink. Note the address space switch upon
        # dereferencing the pointer.
        our_list_entry = physical_eprocess.ActiveProcessLinks.Flink.dereference(
            vm=self.kernel_address_space).Blink.dereference()

        # Now we get the EPROCESS object from the list entry.
        return our_list_entry.dereference_as("_EPROCESS", "ActiveProcessLinks")


