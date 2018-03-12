# -*- coding: utf-8 -*-

from __future__ import division

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'For through-hole devices, placement type must be set to "Through Hole"')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pads_bounds
            * pads_distance
            * right_anchor
        """
        module = self.module

        self.pth_count = len(module.filterPads('thru_hole'))
        self.smd_count = len(module.filterPads('smd'))

        error = False

        if self.pth_count > 0 and module.attribute != 'pth':
            if module.attribute == 'virtual':
                self.warning("Footprint placement type set to 'virtual' - ensure this is correct!")
            # Only THT pads
            elif self.smd_count == 0:
                self.error("Through Hole attribute not set")
                self.errorExtra("For THT footprints, 'Placement type' must be set to 'Through hole'")
                error = True
            # A mix of THT and SMD pads - probably a SMD footprint

        return error


    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            self.info("Setting placement type to 'Through hole'")
            module.attribute = 'pth'
