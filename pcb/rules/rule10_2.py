# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 10.2', 'Doc property contains a full description of footprint.')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        return True if not module.description else False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            # Can't fix this one!
            pass
