# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.12', 'Footprint filters')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        
        filters = self.component.fplist
        
        if len(filters) == 0:
            self.warning("No footprint filters defined")
        
        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("FIX: not supported")
