# -*- coding: utf-8 -*-

def get_pad_1(module):
    for pad in module.pads:
        if pad['number'] == 1:
            return pad

def set_anchor(pads_array, anchor_point):
    for pad in pads_array:
        pad['pos']['x'] -= anchor_point['x']
        pad['pos']['y'] -= anchor_point['y']

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

    set_anchor(module.pads, {'x':xref , 'y':yref})
