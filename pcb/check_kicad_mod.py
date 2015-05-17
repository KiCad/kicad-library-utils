#!/usr/bin/env python

from __future__ import print_function

import argparse
from kicad_mod import *
from print_color import *
import checkrule6_3, checkrule6_9

parser = argparse.ArgumentParser()
parser.add_argument('kicad_mod_files', nargs='+')
parser.add_argument('--fix', help='fix the violations if possible', action='store_true')
parser.add_argument('--nocolor', help='does not use colors to show the output', action='store_true')
parser.add_argument('-v', '--verbose', help='show status of all modules and extra information about the violation', action='store_true')
args = parser.parse_args()

printer = PrintColor(use_color = not args.nocolor)

for filename in args.kicad_mod_files:
    module = KicadMod(filename)

    check6_3 = checkrule6_3.check_rule(module)
    check6_9 = checkrule6_9.check_rule(module)

    # print the violations
    if check6_3 or check6_9:
        printer.green('module: %s' % module.name)

        if check6_3:
            printer.yellow('\tRule 6.3 violated')
            if args.verbose:
                printer.light_blue('\tFor through-hole components, footprint anchor is set on pad 1.')

        if check6_9:
            printer.yellow('\tRule 6.9 violated')
            if args.verbose:
                printer.light_blue('\tValue and reference have a height of 1mm.')
