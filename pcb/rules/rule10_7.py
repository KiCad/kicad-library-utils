# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 10.7', 'All other properties are left to default values. (Move and Place: Free; Auto Place: 0 and 0,  Local Clearance Values: 0)')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        ok=False
        if module.locked:
            self.verbose_message=self.verbose_message+"Module is locked!\n"
            ok=True
        if module.autoplace_cost90 != 0:
            self.verbose_message=self.verbose_message+"Attribute autoplace_cost90 == {0} != 0!\n".format(module.autoplace_cost90)
            ok=True
        if module.autoplace_cost180 != 0:
            self.verbose_message=self.verbose_message+"Attribute autoplace_cost180 == {0} != 0!\n".format(module.autoplace_cost180)
            ok=True
        if module.clearance != 0:
            self.verbose_message=self.verbose_message+"Attribute clearance == {0} != 0!\n".format(module.clearance)
            ok=True
        if module.solder_mask_margin != 0:
            self.verbose_message=self.verbose_message+"Attribute solder_mask_margin == {0} != 0!\n".format(module.solder_mask_margin)
            ok=True
        if module.solder_paste_margin != 0:
            self.verbose_message=self.verbose_message+"Attribute solder_paste_margin == {0} != 0!\n".format(module.solder_paste_margin)
            ok=True
        if module.solder_paste_ratio != 0:
            self.verbose_message=self.verbose_message+"Attribute solder_paste_ratio == {0} != 0!\n".format(module.solder_paste_ratio)
            ok=True
        if module.locked:
            self.verbose_message=self.verbose_message+"Module is locked!\n"
            ok=True
        
        return ok

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.locked = False
            module.autoplace_cost90 = 0
            module.autoplace_cost180 = 0
            module.clearance = 0
            module.solder_mask_margin = 0
            module.solder_paste_margin = 0
            module.solder_paste_ratio = 0
