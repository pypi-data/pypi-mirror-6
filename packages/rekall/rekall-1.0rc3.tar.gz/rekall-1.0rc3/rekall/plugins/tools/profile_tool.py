#!/usr/bin/env python2

# Rekall Memory Forensics
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Author: Michael Cohen scudette@google.com
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

"""
Converts Volatility profile files into the Rekall format.

The Volatility profiles are derived by dumping debugging symbols using various
means into a zip file:

- On Linux the output of dwarfdump is stored and parsed on each execution. The
  constants are just copied from the System map.

- On OSX the symbols are produced using the dsymutil tool while the vtypes are
  python files.

- On Windows the vtypes are python files which must be executed.

Rekall profiles are more structured. All profiles contain a metadata file within
the zip archive called "metadata" which simply contains key value pairs encoded
using json. For example:

{
 # This must point at the implementation of this profile (i.e. the class which
 # should be created). Valid values include Linux32, Linux64, WinXPSP1x86
 # etc. You can use the 'info' plugin to see which classes already exist.

 "ProfileClass": "Linux64"

 # This is the name of a member inside this zip file which contains the
 # constant list.

 "Constants":  "System.map.json"

 # This points at a json file within this zip file which contains the vtype
 # definitions for this profile.

 "VTypes": "vtypes.json"
}

We chose to use json to store the vtype data structures because loading json
files in python is extremely quick and leads to much faster start up times than
having to parse the vtypes in other formats (We do not allow loading of vtypes
inside python files because this may lead to arbitrary code execution since the
vtype file needs to be evaluated.).

Often users already have profiles created for Volatility which they way to use
in Rekall. Rather than fall back to the slow and inefficient parsing of these
profiles, Rekall allows users to convert the old profile into a new, efficient
profile representation. This is what this module does with the convert command.

For example, suppose you have an existing profile created for use in Volatility,
you can just convert it to the rekall format:

./tools/profile_converter.py convert Ubuntu-3.0.0-32-generic-pae.zip \
   Ubuntu-3.0.0-32-generic-pae.rekall.zip

$ ls -l Ubuntu-3.0.0-32-generic-pae.*
-rw-r----- 1 scudette g 643711 Dec 12 02:12 Ubuntu-3.0.0-32-generic-pae.rekall.zip
-rw-r----- 1 scudette g 726480 Dec 12 00:30 Ubuntu-3.0.0-32-generic-pae.zip

Now simply specify the rekall profile using the --profile command line arg.
"""

__author__ = "Michael Cohen <scudette@google.com>"

import logging
import json
import os
import re
import StringIO

from rekall import builtin_profiles
from rekall import io_manager
from rekall import plugin
from rekall import registry

from rekall.plugins.overlays.linux import dwarfdump
from rekall.plugins.overlays.linux import dwarfparser


class ProfileConverter(object):
    """Base class for converters."""

    __metaclass__ = registry.MetaclassRegistry
    __abstract = True

    def __init__(self, input, output, profile_class=None):
        self.input = input
        self.output = output
        self.profile_class = profile_class

    def SelectFile(self, regex):
        """Reads the content of the first file which matches regex."""
        for f in self.input.ListFiles():
            if re.search(regex, f, re.I):
                return self.input.Open(f).read()

    def WriteProfile(self, system_map, vtypes):
        # Sorting the json keys usually achieves much smaller file size due to
        # better compression. Its worth doing it once on conversion.
        self.output.StoreData("Constants.json", system_map)
        self.output.StoreData("vtypes.json", vtypes)
        self.output.StoreData("metadata", dict(
                ProfileClass=self.profile_class,
                Constants="Constants.json",
                VTypes="vtypes.json"))

    def Convert(self):
        raise RuntimeError("Unknown profile format.")

class LinuxConverter(ProfileConverter):
    """Convert an existing Linux profile zip file.

    Since building the linux profile often happens on the target system, where
    Rekall is not normall running, we just convert the result of running Make in
    the tools/linux/ directory. See tools/linux/README for details.

    In short:

    - Run make in tools/linux/ directory. This will build module_dwarf.ko with
      debugging symbols.

    - If you have zip installed, the above step will create the required zip
      file. Otherwise Create a zip file manually with module_dwarf.ko and
      /boot/System.map-`uname -r` (Sometimes when running make not as the root
      user, its not possible to read the System.map file).

    Finally use this tool to convert the profile to a Rekall compatible profile.
    """
    BASE_PROFILE_CLASS = "Linux"

    def ParseSystemMap(self, system_map):
        """Parse the system map and return a list of offset, symbol_name."""
        sys_map = {}
        # get the system map
        for line in system_map.splitlines():
            (address, _, symbol) = line.strip().split()
            try:
                sys_map[symbol] = long(address, 16)
            except ValueError:
                pass

        return sys_map

    def WriteProfile(self, system_map, vtypes):
        """Write all the components needed for the output profile."""
        # Try to guess the bit size of the system if not provided.
        if self.profile_class is None:
            largest_offset = max(system_map.values())
            if largest_offset > 2**32:
                self.profile_class = "%s64" % self.BASE_PROFILE_CLASS
            else:
                self.profile_class = "%s32" % self.BASE_PROFILE_CLASS

        super(LinuxConverter, self).WriteProfile(system_map, vtypes)

    def Convert(self):
        # Check for a linux profile. It should have a System.map in it.
        system_map = self.SelectFile("(^|/)System.map")
        if system_map:
            # Parse the system map file.
            system_map = self.ParseSystemMap(system_map)

            ko_file = self.SelectFile(r"\.ko$")
            if ko_file:
                logging.info("Converting Linux profile with ko module.")
                parser = dwarfparser.DWARFParser(StringIO.StringIO(ko_file))

                # Also write the ko file to ensure we get to keep it.
                with self.output.Create("module.ko") as fd:
                    fd.write(ko_file)

                return self.WriteProfile(system_map, parser.VType())

            dwarf_file = self.SelectFile(r"\.dwarf$")
            if dwarf_file:
                logging.info("Converting Linux profile with dwarf dump output")
                parser = dwarfdump.DWARFParser()
                for line in dwarf_file.splitlines():
                    parser.feed_line(line)

                # The dwarfdump module returns python code so we must exec it.
                l = {}
                exec(parser.print_output(), {}, l)

                return self.WriteProfile(system_map, l["linux_types"])

            # This is here just so we can transform Rekall profiles to Rekall
            # profiles.
            json_file = self.SelectFile(r"\.json$")
            if json_file:
                logging.info("Converting Linux profile with json vtype.")
                return self.WriteProfile(system_map, json.loads(json_file))

        raise RuntimeError("Unknown profile format.")


class OSXConverter(LinuxConverter):
    """Automatic converted for Volatility OSX style profiles.

    You can generate one of those using the instructions here:
    http://code.google.com/p/volatility/wiki/MacMemoryForensics#Building_a_Profile
    """
    BASE_PROFILE_CLASS = "Darwin"

    DLSYM_REGEX = re.compile("([^ ]+) '([^ ]+)'$")

    def ParseSystemMap(self, system_map):
        sys_map = {}
        for line in system_map.splitlines():
            if self.profile_class is None and "Symbol table for" in line:
                last_part = line.split()[-1]
                if last_part == "(x86_64)":
                    self.profile_class = "Darwin64"
                elif last_part == "(i386)":
                    self.profile_class = "Darwin32"
                else:
                    raise RuntimeError(
                        "Unknown Darwin Architecture %s" % last_part)

            # We only care about few things like functions and global symbols.
            if "N_FUN" in line or "EXT" in line or "N_STSYM" in line:
                m = self.DLSYM_REGEX.search(line)
                if m:
                    try:
                        sys_map[m.group(2)] = long(m.group(1), 16)
                    except ValueError:
                        pass

        return sys_map

    def Convert(self):
        # Check for an OSX profile.
        system_map = self.SelectFile("dsymutil$")
        if system_map:
            # Parse the system map file.
            system_map = self.ParseSystemMap(system_map)

            vtype_file = self.SelectFile(r"\.vtypes$")
            if vtype_file:
                logging.info(
                    "Converting Darwin profile with vtypes dump output")

                # The dwarfdump module returns python code so we must exec it.
                l = {}
                exec(vtype_file, {}, l)

                return self.WriteProfile(system_map, l["mac_types"])

            # This is here just so we can transform Rekall profiles to Rekall
            # profiles.
            json_file = self.SelectFile(r"\.json$")
            if json_file:
                logging.info("Converting Darwin profile with json vtype.")
                return self.WriteProfile(system_map, json.loads(json_file))

        raise RuntimeError("Unknown profile format.")


class WindowsConverter(ProfileConverter):
    """A converter from Volatility windows profiles.

    This converter must be manually specified.
    """

    def Convert(self):
        if not self.profile_class:
            raise RuntimeError("Profile class implementation not provided.")

        # The input file is a python file with a data structure in it.
        with open(self.input, "rb") as fd:
            l = {}
            exec(fd.read(), {}, l)

        return self.WriteProfile({}, l["ntkrnlmp_types"])


class ConvertProfile(plugin.Command):
    """Convert a profile from another program to the Rekall format.

    The Rekall profile format is optimized for loading at runtime. This plugin
    produces a Rekall profile from a variety of sources, including:

    - Linux debug compiled kernel module (see tool/linux/README)
    - OSX Dwarfdump outputs.
    """

    __name = "convert_profile"

    @classmethod
    def args(cls, parser):
        """Declare the command line args we need."""
        super(ConvertProfile, cls).args(parser)

        parser.add_argument(
            "--profile_class", default=None,
            help="The name of the profile implementation to specify. "
            "If not specified, we autodetect.")

        parser.add_argument(
            "--converter", default=None,
            help="The name of the converter to use. "
            "If not specified autoguess.")

        parser.add_argument("source",
                            help="Filename of profile to read.")

        parser.add_argument("destination",
                            help="Filename of profile to write.")

    def __init__(self, profile_class=None, converter=None, source=None,
                 destination=None, **kwargs):
        super(ConvertProfile, self).__init__(**kwargs)
        self.profile_class = profile_class
        self.converter = converter
        self.source = source
        self.destination = destination

    def ConvertProfile(self, input, output):
        """Converts the input profile to a new standard profile in output."""
        # First detect what kind of profile the input profile is.
        for converter in (LinuxConverter, OSXConverter):
            try:
                converter(input, output).Convert()
                logging.info("Converted %s to %s", input, output)
                return
            except RuntimeError:
                pass

        raise RuntimeError(
            "No suitable converter found - profile not recognized.")

    def render(self, renderer):
        try:
            output = io_manager.Factory(self.destination, mode="w")
        except IOError:
            logging.critical("Output profile File %s could not be opened.",
                             self.destination)
            return

        if self.converter:
            cls = ProfileConverter.classes.get(self.converter)
            if not cls:
                raise IOError("Unknown converter %s" % self.converter)

            return cls(self.source, output,
                       profile_class=self.profile_class).Convert()

        try:
            input = io_manager.Factory(self.source, mode="r")
        except IOError:
            logging.critical("Input profile file %s could not be opened.",
                             self.source)
            return

        with input, output:
            self.ConvertProfile(input, output)




class ProfileCompressor(object):
    def __init__(self):
        self.data = {}

class CompressProfile(plugin.Command):
    """Reprocess a profile db to produce a new compressed profile container.

    The Rekall builtin profile container contains only the information directly
    used by various plugins. In order to record all the vtype access that
    plugins make, set the environment variable DEBUG_PROFILE to point at a path
    where a json database will be maintained.

    Periodically running this plugin will rebuild the compressed builtin profile
    container by adding further information from this database.
    """
    __name = "update_builtin_profile"

    @classmethod
    def is_active(cls, session):
        """Only active when the DEBUG_PROFILE environment variable is set."""
        return bool(os.environ.get("DEBUG_PROFILE"))

    @classmethod
    def args(cls, parser):
        super(CompressProfile, cls).args(parser)
        parser.add_argument(
            "--output", default="rekall/builtin_profiles.py",
            help="The path to the builtin profile file to be produced.")

    def __init__(self, output=None, **kwargs):
        super(CompressProfile, self).__init__(**kwargs)
        self.output = output
        self.database = os.environ.get("DEBUG_PROFILE")
        self.data = builtin_profiles.BuiltInProfiles.data.copy()

    def Compress(self, compression_db, profile):
        dest = self.data[profile.name] = dict(
            metadata={
            'Constants': 'Constants.json',
            'ProfileClass': profile.__class__.__name__,
            'VTypes': 'vtypes.json',
            })

        constants = compression_db.get("Constants")
        if constants:
            self.CompressConstants(profile.constants, constants, dest)

        self.CompressVTypes(profile.vtypes, compression_db, dest)

    def CompressVTypes(self, profile_vtypes, compression_db, dest):
        for struct, members in compression_db.items():
            profile_struct = profile_vtypes.get(struct)
            if profile_struct:
                size, profile_desc = profile_struct
                out = {}
                dest.setdefault("vtypes.json", {})[struct] = [size, out]

                for member in members:
                    if member in profile_desc:
                        out[member] = profile_desc[member]

    def CompressConstants(self, profile_constants, constants, dest):
        out = dest["Constants.json"] = {}
        for constant in constants:
            if constant in profile_constants:
                out[constant] = profile_constants[constant]

    def PPrint(self, data, depth=0):
        """A pretty printer for a profile.

        This only supports dict, list and non-unicode strings.
        """
        result = []
        if isinstance(data, dict):
            result.append("{")
            for key in sorted(data):
                key = str(key)

                result.append(
                    " %r: %s," % (
                        key, self.PPrint(data[key], depth + 1).strip()))

            result.append("}")

            return "\n".join([(" " * depth + x) for x in result])

        if isinstance(data, list):
            for item in data:
                result.append(self.PPrint(item, depth).strip())

            return "[" + ", ".join(result) + "]"

        if isinstance(data, basestring):
            try:
                data = data.encode("ascii")
            except UnicodeError:
                pass

        return repr(data)

    CODE_TEMPLATE = """
# AUTOGENERATED File do not edit!
# File generated by the profile_tool.py 'compress' command.

from rekall import io_manager


class BuiltInProfiles(io_manager.BuiltInManager):
   data = %s

"""

    def render(self, renderer):
        try:
            # Get the profile access database.
            db = json.load(open(self.database, "rb"))
        except IOError as e:
            logging.error("Unable to open database file: %s", e)
            return

        for name, desc in db.items():
            # Try to open the profile named in the database.
            try:
                source_profile = self.session.LoadProfile(name)
            except ValueError:
                continue

            if source_profile:
                self.Compress(desc, source_profile)

        with open(self.output, "wb") as fd:
            fd.write(self.CODE_TEMPLATE % self.PPrint(self.data))
            logging.info("Wrote compressed profile into %s", self.destination)
