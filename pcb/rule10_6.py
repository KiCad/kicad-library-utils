# -*- coding: utf-8 -*-

from rule import *

class Rule10_6(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule10_6, self).__init__('Rule 10.6', 'All other properties are left to default values. (Move and Place: Free; Auto Place: 0 and 0,  Local Clearance Values: 0)')

    def check(self, module):
        """
        Proceeds the checking of the rule.
        """
        if (module.locked or
            module.autoplace_cost90 != 0 or
            module.autoplace_cost180 != 0 or
            module.clearance != 0 or
            module.solder_mask_margin != 0 or
            module.solder_paste_margin != 0 or
            module.solder_paste_ratio != 0):
            return True

        return False

    def fix(self, module):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check(module):
            module.locked = False
            module.autoplace_cost90 = 0
            module.autoplace_cost180 = 0
            module.clearance = 0
            module.solder_mask_margin = 0
            module.solder_paste_margin = 0
            module.solder_paste_ratio = 0
