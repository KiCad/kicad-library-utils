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
from glob import glob

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

parser.add_argument("--new", help="New (updated) .lib file(s)", nargs='+')
parser.add_argument("--old", help="Old (original) .lib file(s) for comparison", nargs='+')
parser.add_argument("-v", "--verbose", help="Enable extra verbose output", action="store_true")
parser.add_argument("--check", help="Perform KLC check on updated/added components", action='store_true')
parser.add_argument("--nocolor", help="Does not use colors to show the output", action='store_true')
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
        if l.endswith('.lib') and os.path.exists(l):
            new_libs[os.path.basename(l)] = os.path.abspath(l)
            
for lib in args.old:
    libs = glob(lib)
    
    for l in libs:
        if l.endswith('.lib') and os.path.exists(l):
            old_libs[os.path.basename(l)] = os.path.abspath(l)
    
errors = 0            
            
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
        new_cmp[cmp.name] = cmp
        
    for cmp in old_lib.components:
        old_cmp[cmp.name] = cmp
        
    for cmp in new_cmp:
        # Component is 'new' (not in old library)
        if not cmp in old_cmp:
            
            if args.verbose:
                printer.light_green("New symbol '{lib}:{name}'".format(lib=lib_name, name=cmp))
            
            if args.check:
                if not KLCCheck(lib_path, cmp) == 0:
                    errors += 1
        
            continue
            
        chk_new = new_cmp[cmp].checksum
        chk_old = old_cmp[cmp].checksum
        
        if not chk_old == chk_new:

            if args.verbose:
                printer.yellow("Changed symbol '{lib}:{name}'".format(lib=lib_name, name=cmp))
            if args.check:
                if not KLCCheck(lib_path, cmp) == 0:
                    errors += 1
                    
            
        
    for cmp in old_cmp:
        # Component has been deleted from library
        if not cmp in new_cmp:
            if args.verbose:
                printer.red("Removed symbol '{lib}:{name}'".format(lib=lib_name, name=cmp))
            
# Entire lib has been deleted?
for lib_name in old_libs:
    if not lib_name in new_libs:
        if args.verbose:
            printer.red("Removed library '{lib}'".format(lib=lib_name))

# Return the number of errors found ( zero if --check is not set )
sys.exit(errors)
