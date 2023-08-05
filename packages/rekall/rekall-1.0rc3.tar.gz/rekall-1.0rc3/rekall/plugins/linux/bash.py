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


"""Scan for bash history entries.

Based on the algorithm by Andrew Case but greatly optimised for speed.
"""

__author__ = "Michael Cohen <scudette@gmail.com>"

import re
import struct

from rekall import scan
from rekall.plugins.overlays import basic
from rekall.plugins.linux import common


class TimestampScanner(scan.DiscontigScanner, scan.BaseScanner):
    """Search for the realine timestamps.

    These have a special signature which looks like "#" followed by the
    time since the epoch - for example #1384457055.
    """
    def __init__(self, **kwargs):
        super(TimestampScanner, self).__init__(**kwargs)
        self.checks = [
            # We use a quick string search first for this rather unique string.
            ('StringCheck', dict(needle="#")),

            # Refine the search with a more precise regex.
            ('RegexCheck', dict(regex="\#\d{10}")),
            ]


class HistoryScanner(scan.PointerScanner):
    """Scan for the realine history struct.

    This looks for references to the timestamps discovered by the
    TimestampScanner above.
    """
    def __init__(self, task=None, **kwargs):
        super(HistoryScanner, self).__init__(
            address_space=task.get_process_address_space(), **kwargs)
        self.task = task

    def scan(self, **kwargs):
        for hit in super(HistoryScanner, self).scan(**kwargs):
            timestamp_relative_offset = self.profile.get_obj_offset(
                "_hist_entry", "timestamp")

            hist_entry = self.profile._hist_entry(
                offset=hit - timestamp_relative_offset,
                vm=self.address_space)

            yield hist_entry


class HeapHistoryScanner(common.HeapScannerMixIn, HistoryScanner):
    """Only scan for history in the heap."""


class BashProfile64(basic.ProfileLP64, basic.BasicWindowsClasses):
    """Profile to parse internal bash data structures."""

    __abstract = True

    # types come from bash's ./lib/readline/history.h
    bash_vtype_64 = {
        "_hist_entry": [24, {
                "line": [0, ["Pointer", dict(target="String")]],
                "timestamp": [8, ["Pointer", dict(target="String")]],
                "data": [16, ["Pointer", dict(target="String")]],
                }],
        }

    def __init__(self, **kwargs):
        super(BashProfile64, self).__init__(**kwargs)
        self.add_types(self.bash_vtype_64)


class BashProfile32(basic.Profile32Bits, basic.BasicWindowsClasses):
    """Profile to parse internal bash data structures."""

    __abstract = True

    # types come from bash's ./lib/readline/history.h
    bash_vtype_32 = {
        "_hist_entry": [0xC, {
                "line": [0, ["Pointer", dict(target="String")]],
                "timestamp": [4, ["Pointer", dict(target="String")]],
                "data": [8, ["Pointer", dict(target="String")]],
                }],
        }

    def __init__(self, **kwargs):
        super(BashProfile32, self).__init__(**kwargs)
        self.add_types(self.bash_vtype_32)


class BashHistory(common.LinProcessFilter):
    """Scan the bash process for history.

    Based on original algorithm by Andrew Case.
    """
    __name = "bash"

    @classmethod
    def args(cls, parser):
        """Declare the command line args we need."""
        super(BashHistory, cls).args(parser)
        parser.add_argument("--scan_entire_address_space", default=False,
                            action="store_true",
                            help="Scan the entire process address space, "
                            "not only the heap.")

    def __init__(self, scan_entire_address_space=None, **kwargs):
        super(BashHistory, self).__init__(**kwargs)

        self.scan_entire_address_space = scan_entire_address_space
        # If the user did not request any filtering operation we just look at
        # processes which contain "bash".
        if not self.filtering_requested:
            kwargs["proc_regex"] = "bash"
            super(BashHistory, self).__init__(**kwargs)

        if self.profile.metadata("memory_model") == "64bit":
            self.bash_profile = BashProfile64(session=self.session)
        else:
            self.bash_profile = BashProfile32(session=self.session)

    def get_timestamps(self, process):
        """Scan process memory for things that look like a timestamp."""
        results = {}
        process_as = process.get_process_address_space()

        scanner = TimestampScanner(
            profile=self.profile, session=self.session,
            address_space=process_as)

        for hit in scanner.scan():
            timestamp = int(process_as.read(hit+1, 10))
            results[hit] = timestamp

        return results

    def render(self, renderer):
        renderer.table_header([("Pid", "pid", ">6"),
                               ("Name", "name", "<20"),
                               ("Timestamp", "time", "<24"),
                               ("Command", "command", "<20"),
                               ])

        # Choose the correct scanner to use depending on the flags.
        if self.scan_entire_address_space:
            scanner_cls = HistoryScanner
        else:
            scanner_cls = HeapHistoryScanner

        for task in self.filter_processes():
            timestamps = self.get_timestamps(task)
            if not timestamps: continue

            scanner = scanner_cls(
                profile=self.bash_profile, session=self.session,
                pointers=timestamps, task=task)

            hits = sorted(scanner.scan(), key=lambda x: x.timestamp.deref())
            for hit in hits:
                timestamp = self.profile.UnixTimeStamp(
                    value=int(hit.timestamp.deref()[1:]))

                renderer.table_row(task.pid, task.comm, timestamp, hit.line.deref())

