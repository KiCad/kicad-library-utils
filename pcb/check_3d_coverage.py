from __future__ import print_function

import os
from kicad_mod import *
import re
from print_color import *


class Config:

    def __init__(self):

        # "pretty" is a footprint library
        # "pretty name" is the footprint library folder name without extension (e.g. 'Housings_SOIC')

        # "root name" is a directory name from which longer paths are constructed
        # "path name" includes directory name and file name with extension
        # "base name" is file name with extension

        # TODO add arguments for ...
        self.verbose = True
        self.print_colour = True

        self.pretty_root = '/home/ray/KiCad Contributing/'
        self.model_root = '/home/ray/KiCad Contributing/kicad-library/modules/packages3d/'

    def model_dir_name(self, pretty_name):
        return os.path.join(self.model_root, pretty_name + '.3dshapes/')

    def footprint_dir_name(self, pretty_name):
        return os.path.join(self.pretty_root, pretty_name + '.pretty/')

    def valid_pretty_names(self):
        try:
            return sorted([f.split('.')[0] for f in os.listdir(self.pretty_root) if os.path.isdir(os.path.join(self.pretty_root, f)) and f.endswith('.pretty')])
        except FileNotFoundError:
            printer.red('EXIT: module root not found: {mr:s}'.format(mr=self.pretty_root))
            sys.exit(1)

    def valid_models(self, pretty_name):
        try:
            return sorted([model for model in os.listdir(self.model_dir_name(pretty_name)) if model.endswith(('wrl', 'step', 'stp'))])
        except FileNotFoundError:
            printer.red('EXIT: 3D model directory not found: {d:s}'.format(d=self.model_dir_name(pretty_name)))
            sys.exit(1)

    def valid_modules(self, pretty_name):
        dir_name = self.footprint_dir_name(pretty_name)
        try:
            return sorted ([f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f)) and f.endswith('.kicad_mod')])
        except FileNotFoundError:
            printer.red('EXIT: module directory not found: {d:s}'.format(d=dir_name))
            sys.exit(1)


class ReferenceRecord:

    def __init__(self, model_3D, module):
        self.model_3D = model_3D
        self.module = module


def parse_module(filename):

    if config.verbose:
        printer.green('Parsing: {f:s}'.format(f=filename))
    try:
        module = KicadMod(filename)
    except FileNotFoundError:
        printer.red('EXIT: module file not found: {fn:s}'.format(fn=filename))
        sys.exit(1)
    try:
        long_reference = module.models[0]['file']
    except IndexError:
        printer.yellow("- No model file specified: {fn:s}".format(fn=filename))
        return None
    try:
        # Accept both forward and backward slash characters in path
        long_reference = '/'.join(long_reference.split('\\'))
        return os.path.basename(long_reference)
    except:
        printer.yellow("- Invalid model reference: {f:s}".format(f=full))
        return None


def check_footprint_library(pretty_name):

    references = []

    printer.green('\r\nChecking: {p:s}'.format(p=pretty_name))
    for module in config.valid_modules(pretty_name):
        model_ref = parse_module(os.path.join(config.footprint_dir_name(pretty_name), module))
        if model_ref:
            references.append(ReferenceRecord(model_ref, module))
            if config.verbose:
                printer.green('- Reference: {r:s}'.format(r=model_ref)) 

    models = config.valid_models(pretty_name)
    unused = models[:]

    for reference in references:
        if config.verbose:
            printer.green('3D model: {r:s}'.format(r=reference.model_3D))
        if reference.model_3D in models:
            if reference.model_3D in unused:
                unused.remove(reference.model_3D)
        else:
            printer.yellow('- No 3D model for reference {r:s} in module {m:s}'.format(r=reference.model_3D, m=reference.module))

    unused_models = [model for model in unused if model.endswith('.wrl')]
    for model in unused_models:
        printer.yellow('Unused 3D model: {m:s}'.format(m=model))


# main program

config = Config()

printer = PrintColor(use_color=config.print_colour)

for pretty in config.valid_pretty_names():
    check_footprint_library(pretty)

