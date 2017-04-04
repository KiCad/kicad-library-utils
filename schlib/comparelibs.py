#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""

This file compares two .lib files and generates a list of deleted / added / updated components.
This is to be used to compare an updated library file with a previous version to determine which components have been changed.

"""

import argparse
import sys
import os

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

parser.add_argument("--new", help="New (updated) .lib file")
parser.add_argument("--old", help="Old (original) .lib file for comparison")
parser.add_argument("-v", "--verbose", help="Enable extra verbose output", action="store_true")
parser.add_argument("--check", help="Perform KLC check on updated/added components", action='store_true')
parser.add_argument("--nocolor", help="Does not use colors to show the output", action='store_true')

args = parser.parse_args()

if not args.new:
    ExitError("New file not supplied")

if not args.old:
    ExitError("Original file not supplied")

def KLCCheck(component):
    # Wrap library in "quotes" if required
    lib = args.new
    if " " in lib and '"' not in lib:
        lib = '"' + lib + '"'

    call = 'python checklib.py {lib} -c={cmp} -vv -s {nocolor}'.format(
                lib = lib,
                cmp = component,
                nocolor = "--nocolor" if args.nocolor else ""
                )

    return os.system(call)

printer = PrintColor(use_color = not args.nocolor)

new_lib = SchLib( args.new )
old_lib = SchLib( args.old )

# If the libs themselves are unchanged, ignore!
if new_lib.compareChecksum(old_lib):
    # exit silently
    sys.exit(0)

# Dicts of name:checksum pairs
new_chk = {}
old_chk = {}

deleted = []
added = []
updated = []

errors = 0

for cmp in new_lib.components:
    new_chk[cmp.name] = cmp.checksum

for cmp in old_lib.components:
    old_chk[cmp.name] = cmp.checksum

for name in old_chk.keys():
    # First, check if any components have been deleted
    if not name in new_chk:
        deleted.append(name)
        continue

    # Next, check for checksum mismatch
    if not old_chk[name] == new_chk[name]:
        updated.append(name)

# Finally, check for NEW components
for name in new_chk.keys():
    if not name in old_chk:
        added.append(name)

# Display any deleted components
if len(deleted) > 0:
    if args.verbose:
        printer.light_red("Components Removed: {n}".format(n=len(deleted)))
    for cmp in deleted:
        printer.light_red("- " + cmp)

# Display any added components
if len(added) > 0:
    if args.verbose:
        printer.light_green("Components Added: {n}".format(n=len(added)))
    for cmp in added:
        printer.light_green("+ " + cmp)

        # Perform KLC check on component
        if args.check:
            if KLCCheck(cmp) is not 0:
                errors += 1

# Display any updated components
if len(updated) > 0:
    if args.verbose:
        printer.yellow("Components Updated: {n}".format(n=len(updated)))
    for cmp in updated:
        printer.yellow("# " + cmp)

        # perform KLC check on component
        if args.check:
            if KLCCheck(cmp) is not 0:
                errors += 1

if args.verbose and len(deleted) == 0 and len(added) == 0 and len(updated) == 0:
    printer.green("No component variations found")

# Return the number of errors found ( zero if --check is not set )
sys.exit(errors)
