#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script fixes footprint errors where symbols are pointing to footprints
that do not exist.

- Libraries may have been renamed
- Footprints renamed
- Footprint assignment does not match 'libname:fpname' format

A replacement file can be supplied, in JSON format:

{
    // Remap library names
    "library" : {
        "Housings_SOIC" : "Package_SOP",
        "Resistors_SMD" : "Resistor_SMD"
    },

    // Remap footprint names
    "footprint" : {
        "SOIC-8_Pitch1.27" : "SOIC-8_P1.27mm",
        "LED-0805" : "LED0805"
    },

    // Provide footprint libraries for footprints that have none specified
    "prefix" : {
        "SOIC-8" : "Package_SOIC",
    }
}

Library replacements and footprint replacements can be defined therein.

"""

from __future__ import print_function

import argparse
import sys, os
import re
import json

parser = argparse.ArgumentParser(description="Check symbols for footprint errors")

parser.add_argument('-l', '--lib', nargs='+', help='Symbol libraries (.lib files)', action='store')
parser.add_argument('-p', '--pretty', nargs='+', help='Footprint libraries (.pretty dirs)')
parser.add_argument('-r', '--replace', help='Path to JSON file containing replacement information')
parser.add_argument('-v', '--verbose', help='Verbosity level', action='count')
parser.add_argument('-f', '--fix', help='Fix errors', action='store_true')
parser.add_argument('-i', '--interactive', help='Ask user for input when no match found', action='store_true')
parser.add_argument('-m', '--missing', help='Try to assign libraries to footprints which do not specify a library prefix', action='store_true')

args = parser.parse_args()

if not args.verbose:
    args.verbose = 0

verbose = args.verbose

if args.replace:
    with open(args.replace) as json_file:
        replacements = json.loads(json_file.read())

else:
    replacements = {}

# Ensure correct keys
for key in ['library', 'footprint', 'prefix']:
    if not key in replacements:
        replacements[key] = {}

symbol_libs = []
footprint_libs = {}

for lib in args.lib:
    if not os.path.exists(lib) or not lib.endswith('.lib'):
        continue

    symbol_libs.append(lib)

for lib in args.pretty:
    if not os.path.isdir(lib) or not lib.endswith('.pretty'):
        continue

    name = os.path.basename(lib).replace('.pretty', '')

    footprints = []

    for f in os.listdir(lib):
        if not f.endswith('.kicad_mod'):
            continue

        fp = f.replace('.kicad_mod', '')

        footprints.append(fp)

    footprint_libs[name] = footprints

# regex looking for associated footprint
FP = '^F2 "([^"]*)"'

try:
    for lib in symbol_libs:

        output = []

        with open(lib, 'r') as lib_file:
            for line in lib_file:
                result = re.search(FP, line)

                if not result:
                    output.append(line)
                    continue

                footprint = result.groups()[0]

                if len(footprint) <= 1:
                    output.append(line)
                    continue

                # Break footprint into library and name components
                fplib = ""
                fpname = ""

                colon_count = footprint.count(':')

                # Associated footprint is not in the correct format.
                # Skip empty libs
                if colon_count == 0:
                    fpname = footprint

                    if args.missing:
                        # Can we find a prefix for this footprint name?
                        if fpname in replacements['prefix']:
                            fplib = replacements['prefix'][fpname]

                            if args.verbose:
                                print("Prefixing library '{lib}' to '{fp}'".format(
                                    lib=fplib,
                                    fp=fpname))
                        # No default library found for this footprint, ask user?
                        else:
                            if args.verbose:
                                print("No library specified for footprint '{fp}'".format(fp=footprint))
                            if args.interactive:
                                newlib = raw_input("Enter library for footprint '{fp}' (leave blank to skip): ".format(fp=footprint))

                                # Keep track of this for next time
                                replacements['prefix'][fplib] = newlib

                                if newlib:
                                    fplib = newlib
                    else:
                        if args.verbose:
                            print("No library specified for footprint '{fp}'".format(fp=footprint))
                            output.append(line)
                            continue

                elif colon_count > 1:
                    if args.verbose:
                        print("Too many ':' characters in '{fp}'".format(fp=footprint))
                        output.append(line)
                        continue

                else:
                    fplib, fpname = footprint.split(":")

                skip_replace = False

                # If the footprint lib is not found
                if not fplib in footprint_libs:
                    # Try to find a replacement name for the footprint lib
                    if fplib in replacements['library']:
                        newlib = replacements['library'][fplib]

                        # Empty means skip
                        if newlib:
                            fplib = newlib

                    else:
                        if args.verbose:
                            print("No match found for library '{lib}'".format(lib=fplib))
                        if args.interactive:
                            newlib = raw_input("Enter new name for library '{lib}' (leave blank to skip): ".format(lib=fplib))

                            replacements['library'][fplib] = newlib

                            print('lib', fplib, '->', newlib)
                            if newlib:
                                fplib = newlib

                output.append(line)

except KeyboardInterrupt:
    print("User interupted process")

# Save the JSON data if there has been changes from user
if args.interactive and args.replace:
    with open(args.replace, 'w') as json_file:
        json_file.write(json.dumps(replacements, indent=4, sort_keys=True, separators=(',', ':')))