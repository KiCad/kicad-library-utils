#!/usr/bin/env python

"""
This script checks validity of the packages3D paths,
to ensure that the directory structure matches the
.pretty directories (footprint libraries).


"""

from __future__ import print_function

import argparse
import sys, os

parser = argparse.ArgumentParser(description='Check 3D model paths')

parser.add_argument('--pretty', nargs='+', help='List of .pretty footprint directories', action='store')
parser.add_argument('--models', nargs='+', help='List of .3dshapes 3D model directories', action='store')
parser.add_argument('-v', '--verbose', action='count')

args = parser.parse_args()

if not args.verbose:
    args.verbose = 0

pretty = {}

models = {}

for lib in args.pretty:
    if os.path.exists(lib) and lib.endswith('.pretty') and os.path.isdir(lib):
        name = os.path.basename(lib).replace('.pretty', '')
        pretty[name] = os.path.abspath(lib)

for lib in args.models:
    if os.path.exists(lib) and lib.endswith('.3dshapes') and os.path.isdir(lib):
        name = os.path.basename(lib).replace('.3dshapes', '')
        models[name] = os.path.abspath(lib)

if len(pretty) == 0:
    print('No .pretty directories supplied')
    sys.exit(1)

if len(models) == 0:
    print("No .3dshapes directories supplied")
    sys.exit(1)

errors = 0

for m in models:
    if args.verbose:
        print("Checking '{f}'".format(f=m))
    if not m in pretty:
        print("- Mislabeled 3D folder '{f}'".format(f=m))
        errors += 1

        continue

    # We have a matching repo!
    pretty_dir = pretty.get(m, '')

    if not pretty_dir:
        continue

    pretty_files = [f.replace('.kicad_mod', '') for f in os.listdir(pretty_dir) if f.endswith('.kicad_mod')]

    ext = ['.step', '.stp', '.wrl']

    model_dir = models[m]

    model_files = []

    for f in os.listdir(model_dir):

        if not any([f.lower().endswith(x) for x in ext]):
            continue

        # Remove file extension
        m_name = '.'.join(f.split('.')[:-1])
        if not m_name in model_files:
            model_files.append(m_name)

    for mf in model_files:
        if not mf in pretty_files:
            if args.verbose:
                print("- Mislabeled 3D model '{m}'".format(m=mf))
            errors += 1

sys.exit(errors)