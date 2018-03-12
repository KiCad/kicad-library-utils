# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Pin name position offset')

    def check(self):

        offset = int(self.component.definition['text_offset'])

        if offset > 50:
            self.error("Pin offset outside allowed range")
            self.errorExtra("Pin offset ({o}) must not be above 50mils".format(o=offset))
            return True
        elif offset < 20:
            self.warning("Pin offset ouside allowed range")
            self.warningExtra("Pin offset ({o}) should not be below 20mils".format(o=offset))
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing...")
        self.component.draw['rectangles'][0]['thickness'] = '10'
        self.component.draw['rectangles'][0]['fill'] = 'f'

        self.recheck()
