from __future__ import print_function

import os
from kicad_mod import *
import re
from print_color import *


class Config:

    def __init__(self):
        # TODO improve this function
        main_3D_ext = ['wrl']
        other_3D_ext = ['step', 'stp']
        # TODO choose better names
        self.regex_1 = '.*\{ext:s}$'.format(ext=main_3D_ext[0])
        self.regex_2 = '.*\.({ext:s})$'.format(ext='|'.join(main_3D_ext + other_3D_ext))
        # Accept both forward and backward slash characters in path
        self.regex_3 = '[/\\\]([^/\\\]*\.({ext:s}))$'.format(ext='|'.join(main_3D_ext + other_3D_ext))
        self.pretty_path = '../../'
        # self.pretty_path = '/home/ray/KiCad Contributing/'
        self.pretty = 'Housings_SOIC'
        self.module_path = self.pretty_path
        self.three_d_path = '../../kicad-library/modules/packages3d/'
        # self.three_d_path = '/home/ray/KiCad Contributing/kicad-library/modules/packages3d/'
        self.model_3D_path = '{pp:s}{p:s}.3dshapes/'.format(pp=self.three_d_path, p=self.pretty)


class ReferenceRecord:

    def __init__(self, model_3D, module):
        self.model_3D = model_3D
        self.module = module


def parse_module(filename):

    # TODO add verbose control
    # printer.green('Parsing: {f:s}'.format(f=filename))
    try:
        module = KicadMod(filename)
    except FileNotFoundError:
        printer.red('Module file not found: {fn:s}'.format(fn=filename))
        return None
    try:
        full = module.models[0]['file']
    except IndexError:
        printer.yellow("No model file specified: {fn:s}".format(fn=filename))
        return None
    try:
        return re.search(config.regex_3, full).group(1)
    except:
        printer.red("Invalid model reference: {f:s}".format(f=full))
        return None


def check_pretty(config, pretty):

    references = []

    printer.green('\r\nChecking: {p:s}\r\n'.format(p=pretty))
    full_path = config.module_path + pretty
    try:
        for file in os.listdir(full_path):
            if re.match('.*\.kicad_mod$', file):
                reference = parse_module('{mp:s}/{mf:s}'.format(mp=full_path, mf=file))
                if reference:
                    references.append(ReferenceRecord(reference, file))
                    # TODO add verbose control
                    printer.green('Ref: {r:s} From: {m:s}'.format(r=reference, m=file)) 
    except FileNotFoundError:
        printer.red('Module path not found: {mp:s}'.format(mp=config.module_path))
        sys.exit(1)

    models = []

    try:
        for file in os.listdir(config.model_3D_path):
            if re.match(config.regex_2, file):
                models.append(file)
    except FileNotFoundError:
        printer.red('3D model path not found: {mp:s}'.format(mp=config.model_3D_path))
        sys.exit(1)

    unused = models[:]

    for reference in references:
        # TODO add verbose control
        printer.green('3D model: {r:s}'.format(r=reference.model_3D))
        if reference.model_3D in models:
            if reference.model_3D in unused:
                unused.remove(reference.model_3D)
        else:
            printer.red('No 3D model for reference {r:s} in module {m:s}'.format(r=reference.model_3D, m=reference.module))

    for model in unused:
        if re.match(config.regex_1, model):
            printer.red('Unused 3D model: {m:s}'.format(m=model))


# main program

# TODO add colour control
# printer = PrintColor(use_color=not args.nocolor)
printer = PrintColor(use_color=True)

config = Config()

try:
    for folder in os.listdir(config.module_path):
        # TODO handle like other regexes
        if re.match('.*\.pretty$', folder):
            check_pretty(config, folder)
except FileNotFoundError:
    printer.red('Module path not found: {mp:s}'.format(mp=config.module_path))
    sys.exit(1)

