# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 6.9', 'Value and reference have a height of 1mm.')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        if (module.reference['font']['height'] != 1 or module.value['font']['height'] != 1 or
            module.reference['font']['width'] != 1 or module.value['font']['width'] != 1 or
            module.reference['font']['thickness'] != 0.15 or module.value['font']['thickness'] != 0.15):
           return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.reference['font']['height'] = 1
            module.reference['font']['width'] = 1
            module.reference['font']['thickness'] = 0.15

            module.value['font']['height'] = 1
            module.value['font']['width'] = 1
            module.value['font']['thickness'] = 0.15
