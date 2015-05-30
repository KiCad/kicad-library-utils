# -*- coding: utf-8 -*-

from rule import *

class Rule10_3(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule10_3, self).__init__('Rule 10.3', 'Keywords are separated by spaces.')

    def check(self, module):
        """
        Proceeds the checking of the rule.
        """
        return True if module.tags.count(',') > 0 else False

    def fix(self, module):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check(module):
            module.tags = ' '.join(module.tags.replace(' ', '').split(','))
