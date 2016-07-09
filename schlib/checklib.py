#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from schlib import *
from print_color import *
from rules import *

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
parser.add_argument('--fix', help='fix the violations if possible', action='store_true')
parser.add_argument('--nocolor', help='does not use colors to show the output', action='store_true')
parser.add_argument('--enable-extra', help='enable extra checking', action='store_true')
parser.add_argument('-v', '--verbose', help='show status of all components and extra information about the violation', action='count')
parser.add_argument('-s', '--silent', help='If the silent option is set, there will be no output displayed for components with zero violations. This option is useful for checking large libraries', action='count')
args = parser.parse_args()

printer = PrintColor(use_color = not args.nocolor)

# force to be verbose if is looking for a specific component
if not args.verbose and args.component: args.verbose = 1

# get all rules
all_rules = []
for f in dir():
    if f.startswith('rule'):
        all_rules.append(globals()[f].Rule)

# gel all extra checking
all_ec = []
for f in dir():
    if f.startswith('EC'):
        all_ec.append(globals()[f].Rule)

#grab list of libfiles (even on windows!)
libfiles = []

for libfile in args.libfiles:
    libfiles += glob(libfile)

for libfile in libfiles:
    lib = SchLib(libfile)
    n_components = 0
    printer.purple('library: %s' % libfile)
    for component in lib.components:
        # skip components with non matching names
        if args.component and args.component != component.name: continue
        n_components += 1

        

        # check the rules
        n_violations = 0
        for rule in all_rules:
            rule = rule(component)
            if rule.check():
            
                if n_violations == 0: #this is the first violation
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

    if args.fix:
        lib.save()
