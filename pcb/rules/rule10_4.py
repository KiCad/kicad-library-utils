# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 10.4', 'Value is filled with footprint name and is placed on the fabrication layer.')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        return (module.value['value'] != module.name or module.value['layer'] != 'F.Fab')

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.value['value'] = module.name
            module.value['layer'] = 'F.Fab'
