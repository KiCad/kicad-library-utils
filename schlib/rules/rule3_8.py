# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.8', 'Description and keywords properties contains information about the component.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * only_datasheet_missing
        """

        self.only_datasheet_missing = False

        if not self.component.documentation: return True

        if (not self.component.documentation['description'] or
            not self.component.documentation['keywords'] or
            not self.component.documentation['datasheet']):

            if (self.component.documentation['description'] and
                self.component.documentation['keywords'] and
                not self.component.documentation['datasheet']):
                self.only_datasheet_missing = True

            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check():
            # Can't fix that!
            pass
