# -*- coding: utf-8 -*-

def get_pad_1(module):
    for pad in module.pads:
        if pad['number'] == 1:
            return pad

# returns true if a violation is found
def check_rule(module):
    # check if module is through-hole
    if module.attribute == 'pth':
        pad = get_pad_1(module)
        if pad['pos']['x'] != 0 or pad['pos']['y'] != 0:
            return True

    return False

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    pad1 = get_pad_1(module)
    xref = pad1['pos']['x']
    yref = pad1['pos']['y']

    for pad in module.pads:
        pad['pos']['x'] -= xref
        pad['pos']['y'] -= yref
