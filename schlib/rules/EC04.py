# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC04 - Extra Checking', 'Check line width and background for box outlines parts.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * n_rectangles
        """

        # check if component has just one rectangle
        self.n_rectangles = len(self.component.draw['rectangles'])
        if self.n_rectangles != 1: return False

        if (self.component.draw['rectangles'][0]['thickness'] != '10' or
            self.component.draw['rectangles'][0]['fill'] != 'f'):
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check():
            self.component.draw['rectangles'][0]['thickness'] = '10'
            self.component.draw['rectangles'][0]['fill'] = 'f'
