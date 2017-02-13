# -*- coding: utf-8 -*-

from __future__ import division

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 8.1', 'For surface-mount devices, placement type must be set to "Surface Mount"')

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
        
        if self.pth_count > self.smd_count and module.attribute != 'smd':
            self.addMessage("Surface Mount attribute not set")
            return True
            
        return False


    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.attribute = 'smd'
