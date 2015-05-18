# -*- coding: utf-8 -*-

# returns true if a violation is found
def check_rule(module):
    if (module.locked or
        module.autoplace_cost90 != 0 or
        module.autoplace_cost180 != 0 or
        module.clearance != 0 or
        module.solder_mask_margin != 0 or
        module.solder_paste_margin != 0 or
        module.solder_paste_ratio != 0):
        return True

    return False

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    module.locked = False
    module.autoplace_cost90 = 0
    module.autoplace_cost180 = 0
    module.clearance = 0
    module.solder_mask_margin = 0
    module.solder_paste_margin = 0
    module.solder_paste_ratio = 0
