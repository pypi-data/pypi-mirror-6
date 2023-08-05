# Rekall Memory Forensics
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Authors:
# Michael Cohen <scudette@gmail.com>
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

import bisect

from rekall import obj
from rekall.plugins.windows import common


class Modules(common.WindowsCommandPlugin):
    """Print list of loaded modules."""

    __name = "modules"

    # A local cache for find_modules. Key is module base and value is the
    # _LDR_DATA_TABLE_ENTRY for the module.
    mod_lookup = None
    modlist = None

    def __init__(self, **kwargs):
        """List kernel modules by walking the PsLoadedModuleList."""
        super(Modules, self).__init__(**kwargs)

    def lsmod(self):
        """ A Generator for modules (uses _KPCR symbols) """
        if not self.mod_lookup:
            self._make_cache()

        for module in self.mod_lookup.values():
            yield module

    def addresses(self):
        """Returns a list of module addresses."""
        if not self.mod_lookup:
            self._make_cache()

        return sorted(self.mod_lookup.keys())

    def _make_cache(self):
        self.mod_lookup = {}

        ## Try to iterate over the process list in PsActiveProcessHead
        ## (its really a pointer to a _LIST_ENTRY)
        PsLoadedModuleList = self.kdbg.PsLoadedModuleList.dereference_as(
            "_LIST_ENTRY", vm=self.kernel_address_space)

        for l in PsLoadedModuleList.list_of_type("_LDR_DATA_TABLE_ENTRY",
                                                 "InLoadOrderLinks"):
            self.mod_lookup[l.DllBase.v()] = l

        self.modlist = sorted(self.mod_lookup.keys())

    def find_module(self, addr):
        """Uses binary search to find what module a given address resides in.

        This is much faster than a series of linear checks if you have
        to do it many times. Note that modlist and mod_addrs must be sorted
        in order of the module base address."""
        if self.mod_lookup is None:
            self._make_cache()

        addr = int(addr)
        pos = bisect.bisect_right(self.modlist, addr) - 1
        if pos == -1:
            return obj.NoneObject("Unknown")
        mod = self.mod_lookup[self.modlist[pos]]

        if (addr >= mod.DllBase.v() and
            addr < mod.DllBase.v() + mod.SizeOfImage.v()):
            return mod

        return obj.NoneObject("Unknown")

    def render(self, renderer):
        renderer.table_header([("Offset (V)", "offset_v", "[addrpad]"),
                               ("Name", "file_name", "20"),
                               ('Base', "module_base", "[addrpad]"),
                               ('Size', "module_size", "[addr]"),
                               ('File', "path", "")
                               ])

        for module in self.lsmod():
            renderer.table_row(module.obj_offset,
                               module.BaseDllName,
                               module.DllBase,
                               module.SizeOfImage,
                               module.FullDllName)
