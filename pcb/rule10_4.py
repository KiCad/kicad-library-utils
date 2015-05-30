# -*- coding: utf-8 -*-

from rule import *

class Rule10_4(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule10_4, self).__init__('Rule 10.4', 'Value is filled with footprint name and is placed on the fabrication layer.')

    def check(self, module):
        """
        Proceeds the checking of the rule.
        """
        return (module.value['value'] != module.name or module.value['layer'] != 'F.Fab')

    def fix(self, module):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check(module):
            module.value['value'] = module.name
            module.value['layer'] = 'F.Fab'
