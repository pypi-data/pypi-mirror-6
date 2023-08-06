# Rekall Memory Forensics
#
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

from rekall import entity
from rekall import obj

class DarwinProcess(entity.Process):
    @property
    def command(self):
        return self.key_obj.p_comm

    @property
    def pid(self):
        return self.key_obj.pid

    @property
    def ppid(self):
        return self.key_obj.ppid

    @property
    def entity_name(self):
        return self.command

    @property
    def entity_type(self):
        return "Process"


class DarwinOpenHandle(entity.OpenHandle):
    @property
    def resource(self):
        return self.session.get_entity(
            key_obj=self.key_obj.autocast_fg_data()
        )

    @property
    def process(self):
        return self.session.get_entity(
            key_obj=self.meta["proc"],
            entity_cls=DarwinProcess,
        )

    @property
    def descriptor(self):
        return self.meta["fd"]

    @property
    def flags(self):
        return self.meta["flags"]


class DarwinOpenFile(entity.OpenFile):
    @property
    def handle(self):
        if "fileproc" in self.meta:
            return self.session.get_entity(
                key_obj=self.meta["fileproc"],
                entity_cls=DarwinOpenHandle,
            )
        else:
            return obj.NoneObject("Can't find handle without fileproc.")

    @property
    def full_path(self):
        return self.key_obj.full_path

    @property
    def entity_type(self):
        return "Reg. File"

    @property
    def entity_name(self):
        return self.full_path


class DarwinSocket(entity.Connection):
    @property
    def handle(self):
        if "fileproc" in self.meta:
            return self.session.get_entity(
                key_obj=self.meta["fileproc"],
                entity_cls=DarwinOpenHandle
            )
        else:
            return obj.NoneObject("Can't find handle without fileproc.")

    @property
    def addressing_family(self):
        return self.key_obj.addressing_family

    @property
    def entity_name(self):
        return "{} -> {}".format(self.source, self.destination)

    @property
    def entity_type(self):
        return "Sock: {}".format(self.addressing_family)


class DarwinInetSocket(DarwinSocket):
    @property
    def state(self):
        return self.key_obj.tcp_state

    @property
    def protocol(self):
        return self.key_obj.l4_protocol

    @property
    def src_address(self):
        return self.key_obj.src_addr

    @property
    def dst_address(self):
        return self.key_obj.dst_addr

    @property
    def src_port(self):
        return self.key_obj.src_port

    @property
    def dst_port(self):
        return self.key_obj.dst_port

    @property
    def source(self):
        return "{}/{}".format(self.src_address, self.src_port)

    @property
    def destination(self):
        return "{}/{}".format(self.dst_address, self.dst_port)

    @property
    def entity_type(self):
        if self.addressing_family == "AF_INET":
            return "{}v4".format(self.protocol)

        if self.addressing_family == "AF_INET6":
            proto = self.protocol

            # Some v6 protocols are already named with v6 in the name.
            if proto.endswith("6"):
                return proto

            return "{}v6".format(self.protocol)


class DarwinUnixSocket(DarwinSocket):
    @property
    def source(self):
        return "0x%x" % int(self.key_obj.so_pcb)

    @property
    def destination(self):
        return "0x%x" % int(self.key_obj.unp_conn)

    @property
    def entity_name(self):
        return self.key_obj.get_socketinfo_attr("unsi_addr")

    @property
    def entity_type(self):
        return self.key_obj.unix_type

