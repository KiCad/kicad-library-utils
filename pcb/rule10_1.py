# -*- coding: utf-8 -*-

from rule import *
import os

class Rule10_1(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule10_1, self).__init__('Rule 10.1', 'Footprint name must match its filename. (.kicad_mod files).')

    def check(self, module):
        """
        Proceeds the checking of the rule.
        """
        return os.path.splitext(os.path.basename(module.filename))[0] != module.name

    def fix(self, module):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check(module):
            module.name = os.path.splitext(os.path.basename(module.filename))[0]
