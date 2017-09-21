# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Footprint properties should be left to default values.')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module

        err = False

        if module.locked:
            self.error("Module is locked!")
            err = True
        if module.autoplace_cost90 != 0:
            self.warning("Attribute autoplace_cost90 == {0} != 0!".format(module.autoplace_cost90))
        if module.autoplace_cost180 != 0:
            self.warning("Attribute autoplace_cost180 == {0} != 0!".format(module.autoplace_cost180))

        # Following is allowed (with warning) to conform to manufacturer specifications
        if module.clearance != 0:
            self.warning("Attribute clearance == {0} != 0!".format(module.clearance))
        if module.solder_mask_margin != 0:
            self.warning("Attribute solder_mask_margin == {0} != 0!".format(module.solder_mask_margin))
        if module.solder_paste_margin != 0:
            self.warning("Attribute solder_paste_margin == {0} != 0!".format(module.solder_paste_margin))
        if module.solder_paste_ratio != 0:
            self.warning("Attribute solder_paste_ratio == {0} != 0!".format(module.solder_paste_ratio))

        return err

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            self.info("Setting footprint properties to default values")
            module.locked = False
            module.autoplace_cost90 = 0
            module.autoplace_cost180 = 0

            # These might actually be required to match datasheet spec.

            #module.clearance = 0
            #module.solder_mask_margin = 0
            #module.solder_paste_margin = 0
            #odule.solder_paste_ratio = 0
