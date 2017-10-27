#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""

This file looks for components that are duplicated within a library

"""

import argparse
import sys, os

common = os.path.abspath(os.path.join(sys.path[0], '..','common'))

if not common in sys.path:
    sys.path.append(common)

from schlib import *
from print_color import *

#enable windows wildcards
from glob import glob

def ExitError( msg ):
    print(msg)
    sys.exit(-1)

parser = argparse.ArgumentParser(description="Find duplicate parts (including aliases) in a .lib file")

parser.add_argument('libfiles', help=".lib file(s)",nargs="+")
parser.add_argument('-s', '--silent', help='only show errors', action='store_true')
parser.add_argument('--nocolor', help='does not use color', action='store_true')

args = parser.parse_args()

printer = PrintColor(use_color = not args.nocolor)

# Lib files
libfiles = []

for lib in args.libfiles:
    libfiles += glob(lib)

errors = 0
            
for libfile in libfiles:
    lib = SchLib(libfile)
    
    if not args.silent:
        printer.green("Checking {lib}".format(lib=libfile))
    
    
    # dict of { libname : [alias, alias, alias] }
    unique_names = {}
    
    for cmp in lib.components:
    
        alias_list = []
    
        # Check component name
        if cmp.name in unique_names.keys():
            printer.green("Checking {lib}".format(lib=libfile))
        
            printer.yellow("Component '{cmp}' already exists".format(cmp=cmp.name))
            errors += 1
        else:
            # Check each existing alias
            for key in unique_names.keys():
                aliases = unique_names[key]
                
                if cmp.name in aliases:
                    printer.yellow("Component '{cmp}' exists as an alias of '{key}'".format(
                        cmp = cmp.name,
                        key = key ))
                    errors += 1
        
        # Check each alias
        for alias in cmp.aliases.keys():
            alias_list.append(alias)
            if alias in unique_names:
                printer.yellow("Component '{cmp}' ALIAS '{alias}' already exists".format(
                    cmp = cmp.name,
                    alias = alias ))
                errors += 1
                
            # check each alias against all other aliases
            for key in unique_names.keys():
                aliases = unique_names[key]
                
                if alias in aliases:
                    printer.yellow("Component '{cmp}' ALIAS '{alias}' exists as an alias of '{key}'".format(
                        cmp = cmp.name,
                        alias = alias,
                        key = key ))
                    errors += 1
                
        unique_names[cmp.name] = alias_list
            
sys.exit(errors)
