#!/usr/bin/env python

from __future__ import print_function

import argparse

import sys,os

common = os.path.abspath(os.path.join(sys.path[0], '..','common'))

if not common in sys.path:
    sys.path.append(common)
from kicad_mod import *

from print_color import *
from rules import *
from rules.rule import KLCRule

# enable windows wildcards
from glob import glob

parser = argparse.ArgumentParser(description='Checks KiCad footprint files (.kicad_mod) against KiCad Library Convention (KLC v2.0) rules. You can find the KLC at https://github.com/KiCad/kicad-library/wiki/Kicad-Library-Convention')
parser.add_argument('kicad_mod_files', nargs='+')
parser.add_argument('--fix', help='fix the violations if possible', action='store_true')
parser.add_argument('--fixmore', help='fix additional violations, not covered by --fix (e.g. rectangular courtyards), implies --fix!', action='store_true')
parser.add_argument('--rotate', help='rotate the whole symbol by the given number of degrees', action='store', default=0)
parser.add_argument('-r', '--rule', help='specify single rule to check (default = check all rules)', action='store')
parser.add_argument('--nocolor', help='does not use colors to show the output', action='store_true')
parser.add_argument('-v', '--verbose', help='Enable verbose output. -v shows brief information, -vv shows complete information', action='count')
parser.add_argument('-s', '--silent', help='skip output for symbols passing all checks', action='store_true')
parser.add_argument('-e', '--errors', help='Do not suppress fatal parsing errors', action='store_true')

args = parser.parse_args()
if args.fixmore:
    args.fix=True

printer = PrintColor(use_color=not args.nocolor)

exit_code = 0

if args.rule:
    selected_rules = args.rule.split(",")
else:
    selected_rules = None

# get all rules
all_rules = []
for f in dir():
    if f.startswith('rule'):
        if selected_rules == None or (f[4:].replace("_",".") in selected_rules):
            all_rules.append(globals()[f].Rule)
    elif f.startswith('EC'):
        if selected_rules == None or f in selected_rules:
            all_rules.append(globals()[f].Rule)

files = []

for f in args.kicad_mod_files:
    files += glob(f)

if len(files) == 0:
    printer.red("File argument invalid: {f}".format(f=args.kicad_mod_files))
    sys.exit(1)

for filename in files:

    if not os.path.exists(filename):
        printer.red('File does not exist: %s' % filename)
        continue

    if not filename.endswith('.kicad_mod'):
        printer.red('File is not a .kicad_mod : %s' % filename)
        continue

    if args.errors:
        module = KicadMod(filename)
    else:
        try:
            module = KicadMod(filename)
        except Exception as e:
            printer.red('could not parse module: %s' % filename)
            if args.verbose:
                printer.red("Error: " + str(e))
            exit_code += 1
            continue

    if args.rotate!=0:
        module.rotateFootprint(int(args.rotate))
        printer.green('rotated footprint by {deg} degrees'.format(deg=int(args.rotate)))

    n_violations = 0

    no_warnings = True

    output = []

    first = True

    for rule in all_rules:

        rule = rule(module,args)

        error = rule.check()

        if rule.hasOutput():
            if first:
                printer.green("Checking footprint '{fp}':".format(fp=module.name))
                first = False

            printer.yellow("Violating " + rule.name, indentation=2)
            rule.processOutput(printer, args.verbose, args.silent)

        if error:
            n_violations += 1

            if args.fix:
                rule.fix()
                rule.processOutput(printer, args.verbose, args.silent)

    # No messages?
    if first:
        if not args.silent:
            printer.green("Checking footprint '{fp}' - No errors".format(fp=module.name))

    # increment the number of violations
    if n_violations > 0:
        exit_code += 1

    if args.fix or args.rotate!=0:
        module.save()

if args.fix:
    printer.light_red('Some files were updated - ensure that they still load correctly in KiCad')

sys.exit(exit_code)
