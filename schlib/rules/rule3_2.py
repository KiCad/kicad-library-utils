# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, '3.2 - Symbol visual style', 'Symbol visual style')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * n_rectangles
        """
        rectangle_need_fix = False
        # check if component has just one rectangle, if not, skip checking
        self.n_rectangles = len(self.component.draw['rectangles'])
        if self.n_rectangles != 1: return False

        if (self.component.draw['rectangles'][0]['thickness'] != '10'):
            self.error("Component line thickness {0}, recommended {1}".format(self.component.draw['rectangles'][0]['thickness'],10))
            rectangle_need_fix = True
        if (self.component.draw['rectangles'][0]['fill'] != 'f'):
            self.error("Component background filled with {0} color, recommended is {1} color".format(backgroundFillToStr(self.component.draw['rectangles'][0]['fill']),backgroundFillToStr('f')))
            rectangle_need_fix = True

        return True if rectangle_need_fix else False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing...")
        self.component.draw['rectangles'][0]['thickness'] = '10'
        self.component.draw['rectangles'][0]['fill'] = 'f'

        self.recheck()
