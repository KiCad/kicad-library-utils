#!/usr/bin/env python

"""
This script checks the validity of a library table against existing libraries
KiCad maintains the following default library tables:

* Symbols - sym_lib_table
* Footprints - fp_lib_table

It is important that the official libraries match the entries in these tables.

"""

from __future__ import print_function

import argparse
import os
import sys

from lib_table import LibTable

parser = argparse.ArgumentParser(description='Compare a sym-lib-table file against a list of .lib library files')
parser.add_argument('libs', nargs='+', help='.lib files')
parser.add_argument('-t', '--table', help='sym-lib-table file', action='store')

args = parser.parse_args()


def check_entries(lib_table, lib_names):

    errors = 0

    # Check for entries that are incorrectly formatted
    for entry in lib_table.entries:
        nickname = entry['name']
        uri = entry['uri']

        if '\\' in uri:
            print("Found '\\' character in entry '{nick}' - Path separators must be '/'".format(nick=nickname))
            errors += 1

        uri_last = '.'.join(uri.split('/')[-1].split('.')[:-1])

        if not uri_last == nickname:
            print("Nickname '{n}' does not match path '{p}'".format(n=nickname, p=uri))
            errors += 1

    lib_table_names = [entry['name'] for entry in lib_table.entries]

    # Check for libraries that are in the lib_table but should not be
    for name in lib_table_names:
        if not name in lib_names:
            errors += 1
            print("- Extra library '{l}' found in library table".format(l=name))

        if lib_table_names.count(name) > 1:
            errors += 1
            print("- Library '{l}' is duplicated in table".format(l=name))

    # Check for libraries that are not in the lib_table but should be
    for name in lib_names:
        if not name in lib_table_names:
            errors += 1
            print("- Library '{l}' missing from library table".format(l=name))

    # Incorrect lines in the library table
    for error in lib_table.errors:
        errors += 1
        print("- Incorrect line found in library table:")
        print("  - '{line}'".format(line=error))

    return errors


lib_names = []

for lib in args.libs:
    lib_name = '.'.join(os.path.basename(lib).split('.')[:-1])
    lib_names.append(lib_name)

print("Checking library table - '{table}'".format(table=os.path.basename(args.table)))

print("Found {n} libraries".format(n=len(lib_names)))

table = LibTable(args.table)

errors = check_entries(table, lib_names)

sys.exit(errors)
