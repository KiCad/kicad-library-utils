#!/usr/bin/env python
# -*- coding: utf-8 -*-

from schlib import *
import checkrule3_1, checkrule3_2, checkrule3_6
from print_color import *
import argparse

parser = argparse.ArgumentParser(description='Execute checkrule scripts checking 3.* KLC rules in the libraries')
parser.add_argument('libfiles', nargs='+')
parser.add_argument('--nocolor', help='does not use colors to show the output', action='store_true')
parser.add_argument('-v', '--verbose', help='show status of all components and extra information about the violation', action='store_true')
args = parser.parse_args()

printer = PrintColor(use_color = not args.nocolor)

for libfile in args.libfiles:
    lib = SchLib(libfile)
    printer.purple('library: %s' % libfile)
    for component in lib.components:
        check3_1 = checkrule3_1.check_rule(component)
        check3_2 = checkrule3_2.check_rule(component)
        check3_6 = checkrule3_6.check_rule(component)

        if check3_1 or check3_2 or check3_6.count([]) < 3:
            printer.green('component: %s' % component.name)

            if check3_1:
                printer.yellow('\tViolations of rule 3.1')
                if args.verbose:
                    printer.light_blue('\tUsing a 100mils grid, pin ends and origin must lie on grid nodes (IEC-60617).')

                for pin in check3_1:
                    printer.white('\t\tpin: %s (%s), posx %s, posy %s, length: %s' %
                        (pin['name'], pin['num'], pin['posx'], pin['posy'], pin['length']))

            if check3_2:
                printer.yellow('\tViolations of rule 3.2')
                if args.verbose:
                    printer.light_blue('''\tFor black-box symbols, pins have a length of 100mils. Large pin numbers can be\n\taccomodated by incrementing the width in steps of 50mil.''')

                for pin in check3_2:
                    printer.white('\t\tpin: %s (%s), dir: %s, length: %s' %
                        (pin['name'], pin['num'], pin['direction'], pin['length']))

            if check3_6.count([]) < 3:
                printer.yellow('\tViolations of rule 3.6')
                if args.verbose:
                    printer.light_blue('\tField text uses a common size of 50mils.')

                for field in check3_6[0]:
                    namekey = 'reference' if 'reference' in field else 'name'
                    printer.white('\t\tfield: %s, text_size: %s' %
                        (field[namekey], field['text_size']))
                for text in check3_6[1]:
                    printer.white('\t\ttext: %s, text_size: %s' %
                         (text['text'], text['text_size']))
                for pin in check3_6[2]:
                    printer.white('\t\tpin: %s (%s), dir: %s, name_text_size: %s, num_text_size: %s' %
                        (pin['name'], pin['num'], pin['direction'], pin['name_text_size'], pin['num_text_size']))

        elif args.verbose:
            printer.light_green('component: %s......OK' % component.name)
