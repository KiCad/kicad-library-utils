#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from sch import *
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('sch_file', nargs='+')
parser.add_argument('--csv', help='a csv file that will be used to fill the MPN field', action='store')
args = parser.parse_args()
bom = []

if args.csv:
    f = open(args.csv, 'r')
    reader = csv.reader(f)
    header_ok = False
    for row in reader:
        # Try to locate the header row
        if 'Reference(s)' in row and 'MPN' in row:
            header_ok = True
            ref_col = row.index('Reference(s)')
            mpn_col = row.index('MPN')

        elif header_ok:
            bom.append(row)

for f in args.sch_file:
    sch = Schematic(f)

    for component in sch.components:
        if ('#PWR' in component.fields[0]['ref'] or
            'PWR_FLAG' in component.fields[1]['ref']):
            continue

        # create or get the MPN field
        for field in component.fields:
            if field['name'] == '"MPN"':
                break
        else:
            field = component.addField({'name':'"MPN"', 'ref':'"~"'})

        # component reference
        comp_ref = component.fields[0]['ref'].replace('"','')

        # search the component in the BOM items and get the MPN
        for item in bom:
            item_refs = item[ref_col].replace(' ','').split(',')
            if item[mpn_col] and comp_ref in item_refs:
                field['ref'] = '"' + item[mpn_col] + '"'
                break

    sch.save()
