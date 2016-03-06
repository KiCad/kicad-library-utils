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

        self.only_datasheet_missing=False #unused, remove?

        if not self.component.documentation:
            self.verboseOut(Verbosity.HIGH,Severity.ERROR,"missing whole documentation (description, keywords, datasheet)")
            return True

        elif (not self.component.documentation['description'] or
            not self.component.documentation['keywords'] or
            not self.component.documentation['datasheet']):

            if (not self.component.documentation['description']):
                self.verboseOut(Verbosity.HIGH,Severity.ERROR,"missing description")
            if (not self.component.documentation['keywords']):
                self.verboseOut(Verbosity.HIGH,Severity.ERROR,"missing keywords")
            if (not self.component.documentation['datasheet']):
                self.verboseOut(Verbosity.HIGH,Severity.WARNING,"missing datasheet, please provide a datasheet link if it isn't a generic component")
                if (self.component.documentation['description'] and
                    self.component.documentation['keywords']):
                    self.only_datasheet_missing=True
            return True

        else:
            return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.NORMAL, Severity.INFO, "FIX: not supported" )
