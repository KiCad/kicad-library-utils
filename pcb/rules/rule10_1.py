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
        if os.path.splitext(os.path.basename(module.filename))[0] != module.name:
            self.verbose_message=self.verbose_message+"footprint name (in file) was '{0}', but expected (from filename) '{1}'.\n".format(module.name, os.path.splitext(os.path.basename(module.filename))[0])
            return True
        
        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.name = os.path.splitext(os.path.basename(module.filename))[0]
