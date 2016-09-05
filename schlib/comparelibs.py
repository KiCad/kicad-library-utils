#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This file compares two .lib files and generates a list of deleted / added / updated components.
This is to be used to compare an updated library file with a previous version to determine which components have been changed.

"""

import argparse
import sys
from schlib import *
from print_color import *
import os
from glob import glob

parser = argparse.ArgumentParser(description="Compare two .lib files to determine which symbols have changed")

parser.add_argument("--new", help="New (updated) .lib file")
parser.add_argument("--original", help="Original .lib file for comparison")
parser.add_argument("-v", "--verbose", help="Enable extra verbose output", action="store_true")
parser.add_argument("--check", help="Perform KLC check on updated/added components", action='store_true')
parser.add_argument("--nocolor", help="Does not use colors to show the output", action='store_true')
args = parser.parse_args()

def KLCCheck(component, library):
    call = "python3 checklib.py {lib} -c='{cmp}' --enable-extra -s {nocolor}".format(
                lib = library,
                cmp = component,
                nocolor = "--nocolor" if args.nocolor else ""
                )
    
    return os.system(call)

printer = PrintColor(use_color = not args.nocolor)


#grab list of libfiles (even on windows!)
old_libs = []
new_libs = []

#for lib in args.new:
new_libs += glob(args.new)

old_libs += glob(args.original)

deleted = []
added = []
updated = []

errors = 0

for old_lib_path, new_lib_path in zip(old_libs, new_libs):
    # dicts of name:checksum pairs
    new_lib = SchLib(new_lib_path)
    old_lib = SchLib(old_lib_path)

    new_chk = {}
    old_chk = {}

    # Extract name and checksum information
    for c in new_lib.components:
        new_chk[c.name] = c.checksum
    
    for c in old_lib.components:
        old_chk[c.name] = c.checksum
    
    # First, see if any components have been deleted (in OLD but not in NEW)
    for name in old_chk.keys():
        if not name in new_chk:
            deleted.append({'name': name, 'library': old_lib_path})
            continue
        
        # Next, check if there are any component checksum differences
        if not old_chk[name] == new_chk[name]:
            updated.append({'name': name, 'library': new_lib_path})
        
    # Lastly, see if any new components have been added
    for name in new_chk.keys():
        if not name in old_chk:
            added.append({'name': name, 'library': new_lib_path})

# Display any deleted components
if len(deleted) > 0:
    if args.verbose:
        printer.light_red("Components Removed: {n}".format(n=len(deleted)))
    for name in deleted:
        printer.light_red("- " + name)
            
# Display any added components
if len(added) > 0:
    if args.verbose:
        printer.light_green("Components Added: {n}".format(n=len(added)))
    for component in added:
        printer.light_green("+ " + component['name'])

        # Perform KLC check on component
        if args.check:
            if KLCCheck(component['name'], component['library']) is not 0:
                errors += 1
                
# Display any updated components
if len(updated) > 0:
    if args.verbose:
        printer.yellow("Components Updated: {n}".format(n=len(updated)))
    for component in updated:
        printer.yellow("# " + component['name'])

        # perform KLC check on component
        if args.check:
            if KLCCheck(component['name'], component['library']) is not 0:
                errors += 1
            
# Return the number of errors found ( zero if --check is not set )                
sys.exit(errors)
