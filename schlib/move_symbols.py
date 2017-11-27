#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
This script can be used to reorganize symbol libraries
based on regex patterns specified in a JSON file.

Entire libraries can be renamed, or symbols within each
library can be matched and moved

The JSON file should be formatted as such:

{
    "LibName:Cmp*" : "NewLib",

    "EntireLib" : "NewLib2"
}

"""

import shutil
import os
import argparse
import fnmatch
import sys
import glob
import json

import fnmatch

def get_lib_name(pattern):
    return pattern.split(':')[0].lower()

def get_part_filter(pattern):

    s = pattern.split(':')

    # Match all the things!!
    if len(s) < 2:
        return '*'

    return s[1].lower()

def get_output_lib(pattern):
    return PATTERNS[pattern]

def is_entire_lib(pattern):

    """
    Determine if a library pattern designates the entire library
    """

    return get_part_filter(pattern) in ['*', '']


def get_entire_lib_match(lib_name):

    """
    If the library is to be moved entirely,
    return the destination library.
    Otherwise, return None
    """

    lib_name = lib_name.lower()

    for pattern in PATTERNS:
        if not is_entire_lib(pattern):
            continue

        if get_lib_name(pattern) == lib_name:

            op = get_output_lib(pattern)

            # Blank pattern means use current name
            if op == '':
                op = lib_name

            return op

    return None


def get_matches(lib_name, cmp_name):

    lib_name = lib_name.lower()
    cmp_name = cmp_name.lower()

    """
    Return any matches for a lib_name:cmp_name pair
    """

    matches = []

    for pattern in PATTERNS:

        if is_entire_lib(pattern):
            continue

        if not get_lib_name(pattern) == lib_name:
            continue

        part_filter = get_part_filter(pattern)

        # An exact match overrides all other filters
        if part_filter == cmp_name:
            return [get_output_lib(pattern)]

        if fnmatch.fnmatch(cmp_name, part_filter):
            matches.append(get_output_lib(pattern))

    return matches

parser = argparse.ArgumentParser(description='Reorganizing the KiCad libs is fun!')
parser.add_argument('libs', help='List of source libraries', nargs='+')
parser.add_argument('--dest', help='Path to store the output', action='store', default='output')
parser.add_argument('--real', help='Real run (test run by default)', action='store_true')
parser.add_argument('--silent', help='Suppress output messages', action='store_true')
parser.add_argument('--leave', help='Leave unallocated symbols in the library they started in', action='store_true')
parser.add_argument('--clean', help='Clean output directory before running script', action='store_true')
parser.add_argument('-p', '--patterns', help='Path to pattern file (JSON)', action='store')
parser.add_argument('-i', '--interactive', help='Interactive mode', action='store_true')

args = parser.parse_args()

real_mode = args.real

# Import the schlib utils
import schlib

dst_dir = os.path.abspath(args.dest)

# Output dir must exist if real output is to be made
if not os.path.isdir(dst_dir) and args.real:
    print("dest_dir not a valid directory")
    sys.exit(1)

if args.real and args.clean:
    #todo
    pass

if args.patterns:
    with open(args.patterns) as f:
        PATTERNS = json.loads(f.read())
else:
    PATTERNS = {}

# Find the source libraries
src_libs = []
for lib in args.libs:
    src_libs += glob.glob(lib)

# Output libraries
output_libs = {}

allocated_symbols = 0
unallocated_symbols = []
overallocated_symbols = []

def output_lib(name):

    # Case insensitive to reduce mistakes
    for lib in output_libs:
        if name.lower() == lib.lower():
            return output_libs[lib]

    output_libs[name] = schlib.SchLib(os.path.join(dst_dir, name + '.lib'), create=real_mode)

    if not args.silent:
        print("Creating new library - '{n}'".format(n=name))

    return output_libs[name]

# Iterate through all remaining libraries
for src_lib in src_libs:

    lib_name = src_lib.split(os.path.sep)[-1].replace('.lib', '')

    lib = schlib.SchLib(src_lib)

    # Make a copy of each component (so list indexing doesn't get messed up)
    components = [c for c in lib.components]

    # Should this entire library be copied?
    copy_lib = get_entire_lib_match(lib_name)

    if copy_lib is not None:
        if not args.silent:
            print("Copying entire library '{src}' -> '{dst}'".format(src=lib_name, dst=copy_lib))
        if not copy_lib in output_libs:
            output_libs[copy_lib] = schlib.SchLib(os.path.join(dst_dir, copy_lib + '.lib'), create=real_mode)

        out_lib = output_lib(copy_lib)

        for cmp in lib.components:
            out_lib.addComponent(cmp)
            allocated_symbols += 1

        # Skip any further checks
        continue

    for cmp in lib.components:

        # A component should not match more than one filter
        filter_matches = 0

        matches = get_matches(lib_name, cmp.name)

        # No matches found
        if len(matches) == 0:

            if args.leave:
                # Leave the item in the same library it already existed in
                out_lib = output_lib(lib_name)
                out_lib.addComponent(cmp)

                if not args.silent:
                    print("No match found for '{cmp}' - leaving in library '{lib}'".format(cmp = cmp.name, lib=lib_name))

            unallocated_symbols.append(lib_name + ' : ' + cmp.name)
            continue

        # Too many matches!
        if len(matches) > 1:
            overallocated_symbols.append(lib_name + ' : ' + cmp.name)
            continue

        match = matches[0]

        out_lib = output_lib(match)
        out_lib.addComponent(cmp)

        allocated_symbols += 1

        if not args.silent:
            print("{lib} : {name} -> {out}".format(lib=lib_name, name=cmp.name, out=match))


# Save the converted libraries
for key in output_libs:
    lib = output_libs[key]

    if real_mode:
        lib.save()

if len(unallocated_symbols) > 0:
    print("\nUnallocated Symbols:")
    for s in unallocated_symbols:
        print(s)

if len(overallocated_symbols) > 0:
    print("\nOverallocated Symbols:")
    for s in overallocated_symbols:
        print(s)

remaining = len(unallocated_symbols) + len(overallocated_symbols)

print("")

print("Allocated Symbols: {x}".format(x=allocated_symbols))

if remaining > 0:
    print("Symbols remaining: {x}".format(x=remaining))
else:
    print("No symbols remaining! You did well.")
