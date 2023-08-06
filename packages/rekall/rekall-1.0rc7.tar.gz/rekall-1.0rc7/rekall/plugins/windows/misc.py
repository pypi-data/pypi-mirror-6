# Rekall Memory Forensics
#
# Copyright 2014 Google Inc. All Rights Reserved.
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
"""Miscelaneous information gathering plugins."""

__author__ = "Michael Cohen <scudette@google.com>"

from rekall.plugins.windows import common


class WinPhysicalMap(common.WindowsCommandPlugin):
    """Prints the boot physical memory map."""

    __name = "phys_map"

    def render(self, renderer):
        renderer.table_header([
                ("Physical Start", "phys", "[addrpad]"),
                ("Physical End", "phys", "[addrpad]"),
                ("Number of Pages", "pages", "10"),
                ])

        descriptor = self.profile.get_constant_object(
            "MmPhysicalMemoryBlock",
            target="Pointer",
            target_args=dict(
                target="_PHYSICAL_MEMORY_DESCRIPTOR",
                ))

        for memory_range in descriptor.Run:
            renderer.table_row(
                memory_range.BasePage * 0x1000,
                (memory_range.BasePage + memory_range.PageCount) * 0x1000,
                memory_range.PageCount)


class SetProcessContext(common.WinProcessFilter):
    """Set the current process context."""

    __name = "cc"
    interactive = True

    def __enter__(self):
        """Use this plugin as a context manager.

        When used as a context manager we save the state of the address resolver
        and then restore it on exit. This prevents the address resolver from
        losing its current state and makes switching contexts much faster.
        """
        self.process_context = self.session.GetParameter("process_context")
        self.address_resolver_state = self.session.address_resolver.GetState()
        return self

    def __exit__(self, unused_type, unused_value, unused_traceback):
        # Restore the process context.
        self.SwitchProcessContext(self.process_context)
        self.session.address_resolver.SetState(self.address_resolver_state)

    def SwitchProcessContext(self, process=None):
        if process is None:
            message = "Switching to Kernel context\n"
            self.session.SetParameter("default_address_space",
                                      self.session.kernel_address_space)
        else:
            message = ("Switching to process context: {0} "
                       "(Pid {1}@{2:#x})\n").format(
                           process.name, process.pid, process)

            self.session.SetParameter("default_address_space",
                                      process.get_process_address_space())

        # Reset the address resolver for the new context.
        self.session.address_resolver.Reset()
        self.session.SetParameter("process_context", process)

        return message

    def SwitchContext(self):
        if not self.filtering_requested:
            return self.SwitchProcessContext(process=None)

        for process in self.filter_processes():
            return self.SwitchProcessContext(process=process)

        return "Process not found!\n"

    def render(self, renderer):
        message = self.SwitchContext()
        renderer.format(message)



class WinVirtualMap(common.WindowsCommandPlugin):
    """Prints the Windows Kernel Virtual Address Map.

    On 32 bit windows, the kernel virtual address space can be managed
    dynamically. This plugin shows each region and what it is used for.

    Note that on 64 bit windows the address space is large enough to not worry
    about it. In that case, the offsets and regions are hard coded.

    http://www.woodmann.com/forum/entry.php?219-Using-nt!_MiSystemVaType-to-navigate-dynamic-kernel-address-space-in-Windows7
    """

    __name = "virt_map"

    @classmethod
    def is_active(cls, session):
        return (super(WinVirtualMap, cls).is_active(session) and
                session.profile.get_constant('MiSystemVaType'))

    def render(self, renderer):
        renderer.table_header([
            ("Virtual Start", "virt_start", "[addrpad]"),
            ("Virtual End", "virt_end", "[addrpad]"),
            ("Type", "type", "10"),
            ])

        system_va_table = self.profile.get_constant_object(
            "MiSystemVaType",
            target="Array",
            target_args=dict(
                target="Enumeration",
                target_args=dict(
                    target="byte",
                    enum_name="_MI_SYSTEM_VA_TYPE"
                    ),
                )
            )

        system_range_start = self.profile.get_constant_object(
            "MiSystemRangeStart", "unsigned int")

        # The size varies on PAE profiles.
        va_table_size = 0x1000 * 0x1000 / self.profile.get_obj_size("_MMPTE")

        # Coalesce the ranges.
        range_type = range_start = range_length = 0

        for offset in range(system_range_start, 0xffffffff, va_table_size):
            table_index = (offset - system_range_start) / va_table_size
            page_type = system_va_table[table_index]
            if page_type != range_type:
                if range_type:
                    renderer.table_row(
                        range_start, range_start + range_length, range_type)

                range_type = page_type
                range_start = offset
                range_length = va_table_size
            else:
                range_length += va_table_size


class Objects(common.WindowsCommandPlugin):
    """Displays all object Types on the system."""

    name = "object_types"

    def object_types(self):
        type_table = self.profile.get_constant_object(
            "ObpObjectTypes",
            target="Array", target_args=dict(
                target="Pointer",
                count=32,
                target_args=dict(
                    target="_OBJECT_TYPE")
                )
            )

        for t in type_table:
            if t:
                yield t


    def render(self, renderer):
        renderer.table_header(
            [("Index", "idx", ">5"),
             ("Number Objects", "TotalNumberOfObjects", ">15"),
             ("PoolType", "PoolType", "15"),
             ("Name", "name", "")])

        for obj_type in self.object_types():
            renderer.table_row(
                obj_type.Index,
                obj_type.TotalNumberOfObjects,
                obj_type.TypeInfo.PoolType,
                obj_type.Name)


class ImageInfo(common.WindowsCommandPlugin):
    """List overview information about this image."""

    name = "imageinfo"

    def render(self, renderer):
        renderer.table_header([("Fact", "key", "20"),
                               ("Value", "value", "")])

        renderer.table_row(
            "Kernel DTB", "%#x" % self.session.kernel_address_space.dtb)

        resolver = self.session.address_resolver
        for desc, name, type in (
            ("NT Build", "nt!NtBuildLabEx", "String"),
            ("Signed Drivers", "nt!g_CiEnabled", "bool"),
            ):

            renderer.table_row(
                desc, resolver.get_constant_object(name, target=type))

        renderer.section("Physical Layout")
        self.session.plugins.phys_map().render(renderer)
