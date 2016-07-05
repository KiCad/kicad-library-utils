#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from schlib import *
import argparse, sys

parser = argparse.ArgumentParser(description='Moves a component symbol between libraries')
parser.add_argument('name', help='The name of the component to be moved')
parser.add_argument('source', help='The path to the source library')
parser.add_argument('destination', help='The path to the destination library')
parser.add_argument('--create', help='Creates the destination library if does not exists', action='store_true')
args = parser.parse_args()

# check if the component exists in the source
src_lib = SchLib(args.source)
for component in src_lib.components:
    if args.name == component.name:
        break
else:
    print('Error: Cannot find the component in the source library.')
    sys.exit(1)

# open or create destination library
try:
    dst_lib = SchLib(args.destination, args.create)
except FileNotFoundError:
    print('Destination library does not exist. Please, check if path is right or uses create flag to new library.')
    sys.exit(1)

# check if the component exists in the destination
for comp in dst_lib.components:
    if component.name == comp.name:
        print('Error: component "%s" already exists in the destination library.' % (comp.name))
        sys.exit(1)

# append component to destination and save
dst_lib.addComponent(component)
dst_lib.save()

# remove component from source and save
src_lib.removeComponent(component.name)
src_lib.save()

print('Component "%s" moved.'  % (args.name))
print('Please, before commit use git diff to check if everything is ok.')
