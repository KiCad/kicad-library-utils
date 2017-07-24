#!/usr/bin/env python

from __future__ import print_function

import os
import argparse

from kicad_mod import *
from print_color import *

common = os.path.abspath(os.path.join(sys.path[0], '..', 'common'))
if not common in sys.path:
    sys.path.append(common)


# For Python 2 compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = OSError


class Config:

    def __init__(self):

        # "pretty" is a footprint library
        # "pretty name" is the footprint library folder name without extension (e.g. 'Housings_SOIC')

        # "root name" is a directory name from which longer paths are constructed
        # "path name" includes directory name and file name with extension
        # "base name" is file name with extension

        # Set default argument values
        self.use_packages3D = False
        self.verbose = False
        self.print_colour = True
        self.pretty = []
        self.root = '../../'
        self.parse_arguments()
        self.pretty_root = self.root
        self.model_root = os.path.join(self.root, 'packages3D/') if self.use_packages3D else os.path.join(self.root, 'kicad-library/modules/packages3d/')

    def model_dir_name(self, pretty_name):
        return os.path.join(self.model_root, pretty_name + '.3dshapes/')

    def footprint_dir_name(self, pretty_name):
        return os.path.join(self.pretty_root, pretty_name + '.pretty/')

    def valid_pretty_names(self):
        try:
            prettys = sorted([f.split('.')[0] for f in os.listdir(self.pretty_root) if os.path.isdir(os.path.join(self.pretty_root, f)) and f.endswith('.pretty')])
        except FileNotFoundError:
            printer.red('EXIT: problem reading from module root: {mr:s}'.format(mr=self.pretty_root))
            sys.exit(1)
        if self.pretty:
            if self.pretty[0] in prettys:
                return self.pretty
            else:
                printer.red('EXIT: problem reading footprint library: {fl:s}'.format(fl=self.pretty[0]))
                sys.exit(1)
        else:
            return prettys

    def valid_models(self, pretty_name):
        try:
            return sorted([model for model in os.listdir(self.model_dir_name(pretty_name)) if model.endswith(('wrl', 'step', 'stp'))])
        except FileNotFoundError:
            printer.red('- problem reading from 3D model directory: {d:s}'.format(d=self.model_dir_name(pretty_name)))
            return None

    def valid_modules(self, pretty_name):
        dir_name = self.footprint_dir_name(pretty_name)
        try:
            return sorted([f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f)) and f.endswith('.kicad_mod')])
        except FileNotFoundError:
            printer.red('EXIT: problem reading from module directory: {d:s}'.format(d=dir_name))
            sys.exit(1)

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Checks which KiCad footprint files (.kicad_mod) reference 3D model files that exist in the KiCad library.')
        parser.add_argument('-p', '--pretty', help='name of footprint library to check (e.g. Housings_SOIC) (default is all libraries)', type=str, nargs=1)
        parser.add_argument('-r', '--root', help='path to root KiCad folder (defalt is ../../)', type=str, nargs=1)
        parser.add_argument('--usepackages3D', help='check against the packages3D repo instead of kicad-library', action='store_true')
        parser.add_argument('-v', '--verbose', help='enable verbose output', action='store_true')
        parser.add_argument('--nocolour', help='do not use colour text in output', action='store_true')
        args = parser.parse_args()
        if args.verbose:
            self.verbose = True
        if args.nocolour:
            self.print_colour = False
        if args.pretty:
            self.pretty.append(str(args.pretty[0]))
        if args.root:
            self.root = str(args.root[0]) + '/'
        if args.usepackages3D:
            self.use_packages3D = True


class ReferenceRecord:

    def __init__(self, model_3D, module):
        self.model_3D = model_3D
        self.module = module


def parse_module(filename, warnings):

    if config.verbose:
        printer.green('Parsing: {f:s}'.format(f=filename))
    try:
        module = KicadMod(filename)
    except FileNotFoundError:
        printer.red('EXIT: problem reading module file {fn:s}'.format(fn=filename))
        sys.exit(1)
    try:
        long_reference = module.models[0]['file']
    except IndexError:
        printer.yellow("- No model file specified in {fn:s}".format(fn=filename))
        warnings += 1
        return None
    try:
        # Accept both forward and backward slash characters in path
        long_reference = '/'.join(long_reference.split('\\'))
        return os.path.basename(long_reference)
    except:
        printer.yellow("- Invalid model reference {f:s}".format(f=full))
        warnings += 1
        return None


def check_footprint_library(pretty_name):

    references = []
    warning_count = 0

    printer.green('\r\nChecking {p:s} (contains {n:d} modules)'.format(p=pretty_name, n=len(config.valid_modules(pretty_name))))
    for module in config.valid_modules(pretty_name):
        model_ref = parse_module(os.path.join(config.footprint_dir_name(pretty_name), module), warning_count)
        if model_ref:
            references.append(ReferenceRecord(model_ref, module))
            if config.verbose:
                printer.green('- Reference: {r:s}'.format(r=model_ref)) 

    models = config.valid_models(pretty_name)
    if models:
        unused = models[:]
        for reference in references:
            if config.verbose:
                printer.green('3D model: {r:s}'.format(r=reference.model_3D))
            if reference.model_3D in models:
                if reference.model_3D in unused:
                    unused.remove(reference.model_3D)
            else:
                printer.yellow('- No 3D model for reference {r:s} in module {m:s}'.format(r=reference.model_3D, m=reference.module))
                warning_count += 1
        if warning_count > 0:
            printer.yellow('- {n:d} module warnings'.format(n=warning_count))
        unused_models = [model for model in unused if model.endswith('.wrl')]
        for model in unused_models:
            printer.yellow('- Unused ''.wrl'' model {p:s}.3dshapes/{m:s}'.format(p=pretty_name, m=model))
        if len(unused_models) > 0:
            printer.yellow('- {n:d} unused model warnings'.format(n=len(unused_models)))
    else:
        if warning_count > 0:
            printer.yellow('- {n:d} module warnings'.format(n=warning_count))


# main program

config = Config()

printer = PrintColor(use_color=config.print_colour)

if config.verbose:
    printer.green('Pretty root: {r:s}'.format(r=config.pretty_root))
    printer.green('Model root:  {r:s}'.format(r=config.model_root))

for pretty in config.valid_pretty_names():
    check_footprint_library(pretty)

