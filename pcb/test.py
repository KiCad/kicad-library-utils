from kicad_mod import *
import re


def parse_module(filename):

    try:
        module = KicadMod(filename)
    except FileNotFoundError:
        print('Module file not found: {fn:s}'.format(fn=filename))
        return None
    try:
        full = module.models[0]['file']
    except IndexError:
        print("No model file specified.")
        return None
    mat = re.search('/([^/]*\.(wrl|step|stp))$', full)
    if mat:
        return mat.group(1)
    else:
        print("Invalid model reference: {f:s}".format(f=full))
        return None

# main program

ref = parse_module('test.kicad_mod')
if ref:
    print('Adding {r:s} to list.'.format(r=ref))
