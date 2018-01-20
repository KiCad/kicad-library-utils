#!/usr/bin/env python

from __future__ import print_function

import argparse

import sys,os
import re
import glob

regex_str = "\(\s*pad\s*[^\s]+\s*(?:smd|thru_hole)\s*(?:roundrect|custom)"
regex_pattern = re.compile(regex_str)

parser = argparse.ArgumentParser(description='Checks KiCad footprint libs for compatibility with version 4. Outputs a list of incompatible footprints. (optionally removes them to allow the lib to be used with KiCad version 4)')
parser.add_argument('libs', nargs='+')
parser.add_argument('-r', '--remove', help='remove incompatible footprints', action='store_true')

args = parser.parse_args()

invalid = []

for lib in args.libs:
    if not lib.endswith(os.sep):
        lib += os.sep

    #print(glob.glob('{:}*.kicad_mod'.format(lib)))
    for fp in glob.glob('{:}*.kicad_mod'.format(lib)):
        with open(fp, 'r') as fp_file:
            for line in fp_file.readlines():
                if re.search(regex_pattern, line):
                    invalid.append(fp)
                    break

print('\n'.join(invalid))

if args.remove:
    for file in invalid:
        os.remove(file)
