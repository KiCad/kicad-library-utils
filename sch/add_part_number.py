#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from sch import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('sch_file', nargs='+')
parser.add_argument('--fill', help='instead of create a empty field fill it with the \"Value\" field', action='store_true')
args = parser.parse_args()

for f in args.sch_file:
    sch = Schematic(f)

    for component in sch.components:
        value = '~'
        if args.fill:
            value = component.fields[1]['ref']

        MPN = False
        for field in component.fields:
            if field['name'] == '\"MPN\"':
                MPN = True
                break

        if not MPN:
            component.addField({'name':'\"MPN\"', 'ref':value})

    sch.save()
