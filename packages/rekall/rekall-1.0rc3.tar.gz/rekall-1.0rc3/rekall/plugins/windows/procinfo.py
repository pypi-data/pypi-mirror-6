# Rekall Memory Forensics
# Copyright (C) 2012 Michael Cohen
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""This module print details information about PE files and processes.

Output is similar to objdump or pefile.
"""

__author__ = "Michael Cohen <scudette@gmail.com>"

from rekall import args
from rekall import plugin
from rekall import testlib

from rekall.plugins.addrspaces import standard
from rekall.plugins.overlays.windows import pe_vtypes
from rekall.plugins.windows import common


class PEInfo(plugin.Command):
    """Print information about a PE binary."""

    __name = "peinfo"

    @classmethod
    def args(cls, parser):
        super(PEInfo, cls).args(parser)
        parser.add_argument("--image_base", default=0, type=args.IntParser,
                            help="The base of the image.")

        parser.add_argument("--filename", default=None,
                            help="If provided we create an address space "
                            "from this file.")


    def __init__(self, address_space=None, image_base=0, filename=None,
                 **kwargs):
        """Dump a PE binary from memory.

        Status is shown for each exported function:

          - M: The function is mapped into memory.

        Args:
          address_space: The address space which contains the PE image.
          image_base: The address of the image base (dos header).
          filename: If provided we create an address space from this file.
        """
        super(PEInfo, self).__init__(**kwargs)
        self.address_space = address_space
        if filename:
            self.address_space = standard.FileAddressSpace(filename=filename)
        self.image_base = image_base

    def render(self, renderer):
        """Print information about a PE file from memory."""
        try:
            disassembler = self.session.plugins.dis(
                address_space=self.address_space, offset=0,
                session=self.session, length=50)
        except AttributeError:
            disassembler = None

        # Get our helper object to parse the PE file.
        pe_helper = pe_vtypes.PE(address_space=self.address_space,
                                 image_base=self.image_base)

        renderer.table_header([('Machine', 'machine', '<20'),
                               ('TimeDateStamp', 'time', '[wrap:60]')])

        for field in ["Machine", "TimeDateStamp", "Characteristics"]:
            renderer.table_row(field,
                               getattr(pe_helper.nt_header.FileHeader, field))

        renderer.format("\nSections (Relative to 0x{0:08X}):\n",
                        pe_helper.image_base)
        renderer.table_header([('Perm', 'perm', '4'),
                               ('Name', 'name', '<8'),
                               ('VMA', 'vma', '[addrpad]'),
                               ('Size', 'size', '[addrpad]')])

        for permission, name, virtual_address, size in pe_helper.Sections():
            renderer.table_row(permission, name, virtual_address, size)

        renderer.format("\nData Directories:\n")
        renderer.table_header([('', 'name', '<40'),
                               ('VMA', 'vma', '[addrpad]'),
                               ('Size', 'size', '[addrpad]')])

        for d in pe_helper.nt_header.OptionalHeader.DataDirectory:
            renderer.table_row(d.obj_name, d.VirtualAddress, d.Size)


        renderer.format("\nImport Directory (Original):\n")
        renderer.table_header([('Name', 'name', '<50'),
                               ('Ord', 'ord', '5')])

        for dll, name, ordinal in pe_helper.ImportDirectory():
            renderer.table_row(u"%s!%s" % (dll, name), ordinal)

        renderer.format("\nImport Address Table:\n")
        renderer.table_header([('Name', 'name', '<20'),
                               ('Address', 'address', '[addrpad]'),
                               ('Disassembly', 'disassembly', '[wrap:30]')])

        for name, function, ordinal in pe_helper.IAT():
            disassembly = []

            if disassembler:
                for i, (_, _, x) in enumerate(
                    disassembler.disassemble(function)):
                    if i >= 5:
                        break

                    disassembly.append(x.strip())

            renderer.table_row(name, function, "\n".join(disassembly))

        renderer.format("\nExport Directory:\n")
        renderer.table_header([('Entry', 'entry', '[addrpad]'),
                               ('Stat', 'status', '4'),
                               ('Ord', 'ord', '5'),
                               ('Name', 'name', '<50')])

        for dll, function, name, ordinal in pe_helper.ExportDirectory():
            status = 'M' if function.dereference() else "-"
            renderer.table_row(
                function,
                status,
                ordinal,
                u"%s!%s" % (dll, name))

            self.address_space.kb.AddMemoryLocation(int(function), function)

        renderer.format("Version Information:\n")
        renderer.table_header([('key', 'key', '<20'),
                               ('value', 'value', '')])

        for k, v in pe_helper.VersionInformation():
            renderer.table_row(k, v)


class ProcInfo(common.WinProcessFilter):
    """Dump detailed information about a running process."""

    __name = "procinfo"

    def render(self, renderer):
        for task in self.filter_processes():
            renderer.section()
            renderer.format("Pid: %s %s\n",
                            task.UniqueProcessId, task.ImageFileName)

            task_address_space = task.get_process_address_space()
            if not task_address_space:
                renderer.format("Peb Not mapped.\n")
                continue

            renderer.format("\nProcess Environment\n")
            # The environment is just a sentinal terminated array of strings.
            for line in task.Peb.ProcessParameters.Environment:
                renderer.format("   %s\n" % line)

            renderer.format("\nPE Infomation\n")

            # Parse the PE file of the main process's executable.
            pe = PEInfo(address_space=task_address_space,
                        session=self.session,
                        image_base=task.Peb.ImageBaseAddress)

            pe.render(renderer)


class TestProcInfo(testlib.SimpleTestCase):
    PARAMETERS = dict(
        commandline="procinfo --pid=%(pid)s"
        )
