#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from schlib import *
import argparse, sys


# cases covered by this script:
#  (1) resize field text sizes that are not 50mils

class CheckComponent(object):
    def __init__(self, component):
        self.component = component
        self.prerequisites_ok = False
        self.header_printed = False

        self.fieldsToFix = []

        # text sizes have to be 50mils
        for field in component.fields:
            if int(field['text_size']) != 50:
                self.fieldsToFix.append(field)

        self.prerequisites_ok = True

    def print_header(self):
        if not self.header_printed:
            print('\tcomponent: %s' % component.name)
            self.header_printed = True

    def resize_field(self, field):
        self.print_header()
        print('\t\t[resize] field size: %s -> %i' %
            (field['text_size'], 50))
        
        field['text_size'] = "50"

def resize_component_fields(component):
    component = CheckComponent(component)

    # The only case that needs fixing is a text size different than 50mils
    if len(component.fieldsToFix):
        for field in component.fieldsToFix:
            size = int(field['text_size'])

            if size != 0:
                component.resize_field(field)

    return component.header_printed


parser = argparse.ArgumentParser(description='Moves a component symbol between libraries')
parser.add_argument('libfiles', nargs='+')
parser.add_argument('-y', '--apply', help='Apply the suggested modifications in the report', action='store_true')
parser.add_argument('-v', '--verbose', help='Print output for all pins - violating or not', action='store_true')
args = parser.parse_args()

for libfile in args.libfiles:
    lib = SchLib(libfile)
    print('library: %s' % libfile)
    for component in lib.components:
        component_printed = resize_component_fields(component)
        if not component_printed:
            if args.verbose:
                print('\tcomponent: %s......OK' % component.name)

    if args.apply:
        lib.save()
