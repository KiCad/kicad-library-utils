#!/usr/bin/env python

"""
This script renames footprint files (.kicad_mod)
based on a set of provided regex filters.

Renaming is more complicated than just changing the filename.
In addition, the following elements must be renamed:

* Internal name of the footprint
* Any references to the footprint name e.g. on Fab layer
* Reference to 3D model

To provide the regex filters, supply a JSON file with the --regex parameter.

The JSON file should be formatted like this:

{
    "FILTER" : "REPLACEMENT",
    "FILTER" : "REPLACEMENT"
}

e.g.

{
    "TSSOP-([\\d*)_([\\d\\.]*)x([\\d\\.*)_Pitch([\\d\\.]*)mm" : "TSSOP-\\1_\\2x\\3_P\\4mm"
}

"""

from __future__ import print_function

import time
import argparse
import re
import sys,os
import json

common = os.path.abspath(os.path.join(sys.path[0], '..','common'))

if not common in sys.path:
    sys.path.append(common)

# enable windows wildcards
from glob import glob

parser = argparse.ArgumentParser(description="Rename footprint files according to supplied set or regex (regular expressions)")
parser.add_argument('footprints', nargs='+', help="Footprint files (.kicad_mod) to be renamed")
parser.add_argument('--simple', help='Path to simple text replacement file (JSON data)', action='store')
parser.add_argument('--regex', help='Path to regex file (JSON data)', action='store')
parser.add_argument('-r', '--real', help="Perform renaming actions. By default, script performs a dry-run and will not rename any files", action='store_true')
parser.add_argument('-v', '--verbose', help="Print extra debugging information", action='store_true')

args = parser.parse_args()

if not args.regex and not args.simple:
    print("Error: No data file supplied")
    print("Supply regex in JSON file with --regex option")
    print("Supply simple replacement data in JSON file with --simple option")
    sys.exit(1)

if args.regex:
    with open(args.regex) as f:
        json_data = json.loads(f.read())
elif args.simple:
    with open(args.simple) as f:
        json_data = json.loads(f.read())

footprints = []

# Extract all valid footprints supplied to the script
for f in args.footprints:

    for fp in glob(f):
        if not os.path.exists(fp): continue
        if not fp.endswith('.kicad_mod'): continue
        if fp in footprints: continue

        footprints.append(fp)

for f in footprints:

    fp_path = os.path.abspath(f)
    fp_name = os.path.basename(f).replace('.kicad_mod', '')

    fp_dir = os.path.abspath(os.path.dirname(f))

    new_name = None

    if args.regex:
        for pattern in json_data.keys():
            match = re.search(pattern, fp_name)
            if match:
                replacement = json_data[pattern]
                new_name = match.expand(replacement)

                # Break at first match
                break

    elif args.simple:
        for pattern in json_data.keys():
            if pattern in fp_name:
                replacement = json_data[pattern]
                new_name = fp_name.replace(pattern, replacement)

    # Renaming not required. Move on to next footprint
    if not new_name:
        continue

    output = ""

    if args.verbose:
        print(fp_name, '->', new_name)

    with open(fp_path, 'r') as fp_file:
        found_tstamp = False

        for line in fp_file.readlines():
            if not found_tstamp:
                match = re.search(r"\(tedit (\w*)\)", line)

                # Update the timestamp (seconds since epoch)
                if match:
                    found_tstamp = True
                    # Generate a new timestamp
                    tstamp = hex(int(time.time()))[2:].upper()

                    line = re.sub(r"\(tedit \w*\)", "(tedit " + tstamp + ")", line)

            # Simple text substitution
            line = line.replace(fp_name, new_name)

            output += line

        if args.real:
            new_file = os.path.join(fp_dir, new_name + ".kicad_mod")

            # Write new file
            with open(new_file, 'w') as f:
                f.write(output)

            # Delete old file
            os.remove(fp_path)

