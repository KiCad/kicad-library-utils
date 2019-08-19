#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

"""

This file compares two .lib files and generates a list of deleted / added / updated components.
This is to be used to compare an updated library file with a previous version to determine which components have been changed.

"""

import argparse
import sys
import os
from glob import glob
import fnmatch

# Path to common directory
common = os.path.abspath(os.path.join(sys.path[0], '..','common'))

if not common in sys.path:
    sys.path.append(common)

from schlib import *
from print_color import *

def ExitError( msg ):
    print(msg)
    sys.exit(-1)

parser = argparse.ArgumentParser(description="Compare two .lib files to determine which symbols have changed")

parser.add_argument("--new", help="New (updated) .lib file(s), or folder of .lib files", nargs='+')
parser.add_argument("--old", help="Old (original) .lib file(s), or folder of .lib files for comparison", nargs='+')
parser.add_argument("-v", "--verbose", help="Enable extra verbose output", action="store_true")
parser.add_argument("--check", help="Perform KLC check on updated/added components", action='store_true')
parser.add_argument("--nocolor", help="Does not use colors to show the output", action='store_true')
parser.add_argument("--design-breaking-changes", help="Checks if there have been changes made that would break existing designs using a particular symbol.", action='store_true')
parser.add_argument("--check-aliases", help="Do not only check symbols but also aliases.", action='store_true')
parser.add_argument("--shownochanges", help="Show libraries that have not changed", action="store_true")

args,extra = parser.parse_known_args()

if not args.new:
    ExitError("New file(s) not supplied")

if not args.old:
    ExitError("Original file(s) not supplied")

def KLCCheck(lib, component):

    # Wrap library in "quotes" if required
    if " " in lib and '"' not in lib:
        lib = '"' + lib + '"'

    call = 'python checklib.py {lib} -c={cmp} -vv -s {nocolor}'.format(
                lib = lib,
                cmp = component,
                nocolor = "--nocolor" if args.nocolor else ""
                )

    # Pass extra arguments to checklib script
    if len(extra) > 0:
        call += ' '.join([str(e) for e in extra])

    return os.system(call)

printer = PrintColor(use_color = not args.nocolor)

new_libs = {}
old_libs = {}

for lib in args.new:
    libs = glob(lib)

    for l in libs:
        if os.path.isdir(l):
            for root, dirnames, filenames in os.walk(l):
                for filename in fnmatch.filter(filenames, '*.lib'):
                    new_libs[os.path.basename(filename)] = os.path.abspath(os.path.join(root, filename))

        elif l.endswith('.lib') and os.path.exists(l):
            new_libs[os.path.basename(l)] = os.path.abspath(l)

for lib in args.old:
    libs = glob(lib)

    for l in libs:
        if os.path.isdir(l):
            for root, dirnames, filenames in os.walk(l):
                for filename in fnmatch.filter(filenames, '*.lib'):
                    old_libs[os.path.basename(filename)] = os.path.abspath(os.path.join(root, filename))

        elif l.endswith('.lib') and os.path.exists(l):
            old_libs[os.path.basename(l)] = os.path.abspath(l)

errors = 0
design_breaking_changes = 0

for lib_name in new_libs:

    lib_path = new_libs[lib_name]
    new_lib = SchLib(lib_path)


    # New library has been created!
    if not lib_name in old_libs:

        if args.verbose:
            printer.light_green("Created library '{lib}'".format(lib=lib_name))

        # Check all the components!
        for cmp in new_lib.components:

            if args.check:
                if not KLCCheck(lib_path, cmp.name) == 0:
                    errors += 1


        continue

    # Library has been updated - check each component to see if it has been changed
    old_lib_path = old_libs[lib_name]
    old_lib = SchLib(old_lib_path)

    # If library checksums match, we can skip entire library check
    if new_lib.compareChecksum(old_lib):
        if args.verbose and args.shownochanges:
            printer.yellow("No changes to library '{lib}'".format(lib=lib_name))
        continue

    new_cmp = {}
    old_cmp = {}

    for cmp in new_lib.components:
        new_cmp[cmp.name] = {'cmp': cmp, 'alias_of': None}
        if args.check_aliases:
            for alias in cmp.aliases:
                new_cmp[alias] = {'cmp': cmp, 'alias_of': cmp.name}

    for cmp in old_lib.components:
        old_cmp[cmp.name] = {'cmp': cmp, 'alias_of': None}
        if args.check_aliases:
            for alias in cmp.aliases:
                old_cmp[alias] = {'cmp': cmp, 'alias_of': cmp.name}

    for cmp in new_cmp:
        # Component is 'new' (not in old library)
        alias_info = ''
        if new_cmp[cmp]['alias_of']:
            alias_info = ' alias of {}'.format(new_cmp[cmp]['alias_of'])

        if not cmp in old_cmp:

            if args.verbose:
                printer.light_green("New '{lib}:{name}'{alias_info}".format(
                    lib=lib_name, name=cmp, alias_info=alias_info))

            if args.check:
                if not KLCCheck(lib_path, cmp) == 0:
                    errors += 1

            continue

        if new_cmp[cmp]['alias_of'] != old_cmp[cmp]['alias_of'] and args.verbose:
            printer.white("Changed alias state of '{lib}:{name}'".format(lib=lib_name, name=cmp))

        chk_new = new_cmp[cmp]['cmp'].checksum
        chk_old = old_cmp[cmp]['cmp'].checksum

        if not chk_old == chk_new:
            if args.verbose:
                printer.yellow("Changed '{lib}:{name}'{alias_info}".format(
                    lib=lib_name, name=cmp, alias_info=alias_info))
            if args.design_breaking_changes:
                pins_moved = 0
                nc_pins_moved = 0
                pins_missing = 0
                nc_pins_missing = 0
                for pin_old in old_cmp[cmp]['cmp'].pins:
                    pin_new = new_cmp[cmp]['cmp'].getPinByNumber(pin_old['num'])
                    if pin_new is None:
                        if pin_old['electrical_type'] == 'N' and pin_new['electrical_type'] == 'N':
                            nc_pins_missing +=1
                        else:
                            pins_missing += 1
                        continue

                    if pin_old['posx'] != pin_new['posx'] or pin_old['posy'] != pin_new['posy']:
                        if pin_old['electrical_type'] == 'N' and pin_new['electrical_type'] == 'N':
                            nc_pins_moved +=1
                        else:
                            pins_moved += 1

                if pins_moved > 0 or pins_missing > 0:
                    design_breaking_changes += 1
                    printer.light_purple("Pins have been moved, renumbered or removed in symbol '{lib}:{name}'{alias_info}".format(
                        lib=lib_name, name=cmp, alias_info=alias_info))
                elif nc_pins_moved > 0 or nc_pins_missing > 0:
                    design_breaking_changes += 1
                    printer.purple("Normal pins ok but NC pins have been moved, renumbered or removed in symbol '{lib}:{name}'{alias_info}".format(
                        lib=lib_name, name=cmp, alias_info=alias_info))

            if args.check:
                if not KLCCheck(lib_path, cmp) == 0:
                    errors += 1

    for cmp in old_cmp:
        # Component has been deleted from library
        if not cmp in new_cmp:
            alias_info = ''
            if old_cmp[cmp]['alias_of']:
                alias_info = ' was an alias of {}'.format(old_cmp[cmp]['alias_of'])

            if args.verbose:
                printer.red("Removed '{lib}:{name}'{alias_info}".format(
                    lib=lib_name, name=cmp, alias_info=alias_info))
            if args.design_breaking_changes:
                design_breaking_changes += 1

# Entire lib has been deleted?
for lib_name in old_libs:
    if not lib_name in new_libs:
        if args.verbose:
            printer.red("Removed library '{lib}'".format(lib=lib_name))
        if args.design_breaking_changes:
            design_breaking_changes += 1

# Return the number of errors found ( zero if --check is not set )
sys.exit(errors + design_breaking_changes)
