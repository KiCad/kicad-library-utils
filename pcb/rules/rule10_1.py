# -*- coding: utf-8 -*-

from rules.rule import *
import os

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 10.1', 'Footprint name must match its filename. (.kicad_mod files).')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        return os.path.splitext(os.path.basename(module.filename))[0] != module.name

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.name = os.path.splitext(os.path.basename(module.filename))[0]
