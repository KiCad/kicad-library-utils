#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from schlib import *
from print_color import *
import re
from rules import *
from rules.rule import KLCRule

#enable windows wildcards
from glob import glob

def processVerboseOutput(messageBuffer):
    if args.verbose:
        for msg in messageBuffer:
            if msg[1] <= args.verbose:
                if msg[2]==0:#Severity.INFO
                    printer.gray(msg[0], indentation=4)
                elif msg[2]==1:#Severity.WARNING
                    printer.brown(msg[0], indentation=4)
                elif msg[2]==2:#Severity.ERROR
                    printer.red(msg[0], indentation=4)
                elif msg[2]==3:#Severity.SUCCESS
                    printer.green(msg[0], indentation=4)
                else:
                    printer.red("unknown severity: "+msg[2], indentation=4)

parser = argparse.ArgumentParser(description='Execute checkrule scripts checking 3.* KLC rules in the libraries')
parser.add_argument('libfiles', nargs='+')
parser.add_argument('-c', '--component', help='check only a specific component (implicitly verbose)', action='store')
parser.add_argument('-p', '--pattern', help='Check multiple components by matching a regular expression', action='store')
parser.add_argument('-r','--rule',help='Select a particular rule (or rules) to check against (default = all rules). Use comma separated values to select multiple rules. e.g. "-r 3.1,EC02"')
parser.add_argument('--fix', help='fix the violations if possible', action='store_true')
parser.add_argument('--nocolor', help='does not use colors to show the output', action='store_true')
parser.add_argument('--enable-extra', help='enable extra checking', action='store_true')
parser.add_argument('-v', '--verbose', help='show status of all components and extra information about the violation', action='count')
parser.add_argument('-s', '--silent', help='skip output for symbols passing all checks', action='store_true')

args = parser.parse_args()

printer = PrintColor(use_color = not args.nocolor)

# force to be verbose if is looking for a specific component
if not args.verbose and args.component: args.verbose = 1

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

# gel all extra checking
all_ec = []
for f in dir():
    if f.startswith('EC'):
        if (selected_rules is None) or (f.lower() in [r.lower() for r in selected_rules]):
            all_ec.append(globals()[f].Rule)
            #force --enable-extra on if an EC rule is selected
            if selected_rules is not None:
                args.enable_extra = True

#grab list of libfiles (even on windows!)
libfiles = []

for libfile in args.libfiles:
    libfiles += glob(libfile)

exit_code = 0

for libfile in libfiles:
    lib = SchLib(libfile)
    n_components = 0

    # Print the library name if multiple libraries have been passed
    if len(libfiles) > 1:
        printer.purple('library: %s' % libfile)

    for component in lib.components:
        # skip components with non matching names

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
        for rule in all_rules:
            rule = rule(component)
            if rule.check():
                #this is the first violation
                if n_violations == 0:
                    printer.green('checking component: %s' % component.name)

                n_violations += 1
                printer.yellow('Violating ' +  rule.name, indentation=2)
                if args.verbose:
                    printer.light_blue(rule.description, indentation=4, max_width=100)

                if args.fix:
                    rule.fix()

                processVerboseOutput(rule.messageBuffer)

        # extra checking
        if args.enable_extra:
            for ec in all_ec:
                ec = ec(component)
                if ec.check():
                    if n_violations == 0: #this is the first violation
                        printer.green('checking component: %s' % component.name)
                    n_violations += 1
                    printer.yellow('Violating ' +  ec.name, indentation=2)

                    if args.verbose:
                        printer.light_blue(ec.description, indentation=4, max_width=100)

                    if args.fix:
                        ec.fix()

                    processVerboseOutput(ec.messageBuffer)

        # check the number of violations
        if n_violations == 0 and not args.silent:
            printer.light_green('Component: {cmp}'.format(cmp=component.name))
            printer.light_green('No violations found', indentation=2)
        else:
            exit_code += 1

    if args.fix:
        lib.save()

sys.exit(exit_code);
