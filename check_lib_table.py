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
import re
import os
import sys

parser = argparse.ArgumentParser(description='Compare a sym_lib_table file against a list of .lib library files')
parser.add_argument('libs', nargs='+', help='.lib files')
parser.add_argument('-t', '--table', help='sym_lib_table file', action='store')

args = parser.parse_args()

class LibTable:

    def __init__(self, filename):

        RE_NAME = r'\(name "?([^\)"]*)"?\)'
        RE_TYPE = r'\(type "?([^\)"]*)"?\)'
        RE_URI  = r'\(uri "?([^\)"]*)"?\)'
        RE_OPT  = r'\(options "?([^\)"]*)"?\)'
        RE_DESC = r'\(descr "?([^\)"]*)"?'

        self.entries = []
        self.errors = []

        with open(filename, 'r') as lib_table_file:

            for line in lib_table_file:

                # Skip lines that do not define a library
                if not '(lib ' in line:
                    continue

                re_name = re.search(RE_NAME, line)
                re_type = re.search(RE_TYPE, line)
                re_uri  = re.search(RE_URI,  line)
                re_opt  = re.search(RE_OPT,  line)
                re_desc = re.search(RE_DESC, line)

                if re_name and re_type and re_uri and re_opt and re_desc:
                    entry = {}
                    entry['name'] = re_name.groups()[0]
                    entry['type'] = re_type.groups()[0]
                    entry['uri']  = re_uri.groups()[0]
                    entry['opt']  = re_opt.groups()[0]
                    entry['desc'] = re_desc.groups()[0]

                    self.entries.append(entry)

                else:
                    self.errors.append(line)

    def check_entries(self, lib_names):

        errors = 0

        # Check for entries that are incorrectly formatted
        for entry in self.entries:
            nickname = entry['name']
            uri = entry['uri']

            if '\\' in uri:
                print("Found '\\' character in entry '{nick}' - Path separators must be '/'".format(nick=nickname))
                errors += 1

            uri_last = '.'.join(uri.split('/')[-1].split('.')[:-1])

            if not uri_last == nickname:
                print("Nickname '{n}' does not match path '{p}'".format(n=nickname, p=uri))
                errors += 1

        lib_table_names = [entry['name'] for entry in self.entries]

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
        for error in self.errors:
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

errors = table.check_entries(lib_names)

sys.exit(errors)