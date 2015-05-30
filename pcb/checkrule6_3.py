# -*- coding: utf-8 -*-

# returns true if a violation is found
def check_rule(module):
    # check if module is through-hole
    if module.attribute == 'pth':
        pad = module.getPadsByNumber(1)[0]
        if pad['pos']['x'] != 0 or pad['pos']['y'] != 0:
            return True

    return False

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    pad1 = module.getPadsByNumber(1)[0]
    module.setAnchor((pad1['pos']['x'], pad1['pos']['y']))
