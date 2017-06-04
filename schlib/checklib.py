#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys, os

common = os.path.abspath(os.path.join(sys.path[0], '..','common'))

if not common in sys.path:
    sys.path.append(common)
    
from schlib import *

from print_color import *
import re
from rules import *
from rules.rule import KLCRule

#enable windows wildcards
from glob import glob

parser = argparse.ArgumentParser(description='Checks KiCad library files (.lib) against KiCad Library Convention (KLC v2.0) rules. You can find the KLC at https://github.com/KiCad/kicad-library/wiki/Kicad-Library-Convention')
parser.add_argument('libfiles', nargs='+')
parser.add_argument('-c', '--component', help='check only a specific component (implicitly verbose)', action='store')
parser.add_argument('-p', '--pattern', help='Check multiple components by matching a regular expression', action='store')
parser.add_argument('-r','--rule',help='Select a particular rule (or rules) to check against (default = all rules). Use comma separated values to select multiple rules. e.g. "-r 3.1,EC02"')
parser.add_argument('--fix', help='fix the violations if possible', action='store_true')
parser.add_argument('--nocolor', help='does not use colors to show the output', action='store_true')
parser.add_argument('-v', '--verbose', help='Enable verbose output. -v shows brief information, -vv shows complete information', action='count')
parser.add_argument('-s', '--silent', help='skip output for symbols passing all checks', action='store_true')

args = parser.parse_args()

printer = PrintColor(use_color = not args.nocolor)

# set verbosity globally
KLCRule.verbosity = args.verbose

#user can select various rules
#in the format -r=3.1 or --rule=3.1,EC01,EC05
if args.rule:
    selected_rules = args.rule.split(',')
else:
    #ALL rules are used
    selected_rules = None

# get all rules
all_rules = []
for f in dir():
    if f.startswith('rule'):
        #f is of the format rule3_1 (user may have speicified a rule like 3.1)
        if (selected_rules == None) or (f[4:].replace("_",".") in selected_rules):
            all_rules.append(globals()[f].Rule)

# add all extra checking
for f in dir():
    if f.startswith('EC'):
        if (selected_rules is None) or (f.lower() in [r.lower() for r in selected_rules]):
            all_rules.append(globals()[f].Rule)

#grab list of libfiles (even on windows!)
libfiles = []

if len(all_rules)<=0:
    printer.red("No rules selected for check!")
    sys.exit(1)
else:
    if (args.verbose>2):
        printer.regular("checking rules:")	
        for rule in all_rules:
            printer.regular("  - "+str(rule))
        printer.regular("")	



for libfile in args.libfiles:
    libfiles += glob(libfile)

if len(libfiles) == 0:
    printer.red("File argument invalid: {f}".format(f=args.libfiles))
    sys.exit(1)
    
exit_code = 0

for libfile in libfiles:
    lib = SchLib(libfile)
    n_components = 0

    # Print library name
    if len(libfiles) > 1:
        printer.purple('Library: %s' % libfile)

    for component in lib.components:
        
        #simple match
        match = True
        if args.component:
            match = match and args.component.lower() == component.name.lower()

        #regular expression match
        if args.pattern:
            match = match and re.search(args.pattern, component.name, flags=re.IGNORECASE)

        if not match: continue

        n_components += 1

        # check the rules
        n_violations = 0

        first = True
    
        for rule in all_rules:
            rule = rule(component)
            if (args.verbose>2):
                printer.white("checking rule "+rule.name)	
            
            error = rule.check()
            
            if rule.hasOutput():
                if first:
                    printer.green("Checking symbol '{sym}':".format(sym=component.name))
                    first = False
                    
                printer.yellow("Violating " + rule.name, indentation=2)
                rule.processOutput(printer, args.verbose, args.silent)
            
            # Specifically check for errors
            if error:
                n_violations += 1

                if args.fix:
                    rule.fix()
                    rule.processOutput(printer, args.verbose, args.silent)
            
        # No messages?
        if first:
            if not args.silent:
                printer.green("Checking symbol '{sym}' - No errors".format(sym=component.name))
            
        # check the number of violations
        if n_violations > 0:
            exit_code += 1

    if args.fix:
        lib.save()
		
sys.exit(exit_code);
