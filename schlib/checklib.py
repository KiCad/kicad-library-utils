#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from schlib import *
import checkrule3_1, checkrule3_2, checkrule3_6
import argparse

parser = argparse.ArgumentParser(description='Execute the checkrule scripts to check the KLC in the libraries')
parser.add_argument('libfiles', nargs='+')
parser.add_argument('-v', '--verbose', help='Print output for all pins - violating or not', action='store_true')
args = parser.parse_args()

for libfile in args.libfiles:
    lib = SchLib(libfile)
    print('library: %s' % libfile)
    for component in lib.components:
        component_printed = False
        component_printed = checkrule3_1.check_rule(component, component_printed)
        component_printed = checkrule3_2.check_rule(component, component_printed)
        component_printed = checkrule3_6.check_rule(component, component_printed)
        if not component_printed:
            if args.verbose:
                print('\tcomponent: %s......OK' % component.name)
