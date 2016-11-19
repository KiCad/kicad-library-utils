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
        invalid_documentation = 0

        #check part itself
        if self.checkDocumentation(self.component.name, self.component.documentation):
            invalid_documentation += 1

        #check all its aliases too
        if self.component.aliases:
            for alias in self.component.aliases.keys():
                self.verboseOut(Verbosity.HIGH,Severity.INFO,"checking alias: {0}".format(alias))
                if self.checkDocumentation(alias, self.component.aliases[alias], indentation=2):
                    invalid_documentation+=1

        return True if invalid_documentation>0 else False


    def checkDocumentation(self, name, documentation, indentation=0):
        if not documentation:
            self.verboseOut(Verbosity.HIGH,Severity.ERROR," "*indentation+"missing whole documentation (description, keywords, datasheet)")
            return True

        elif (not documentation['description'] or
            not documentation['keywords'] or
            not documentation['datasheet']):

            if (not documentation['description']):
                self.verboseOut(Verbosity.HIGH,Severity.ERROR," "*indentation+"missing description")
            if (not documentation['keywords']):
                self.verboseOut(Verbosity.HIGH,Severity.ERROR," "*indentation+"missing keywords")
            if (not documentation['datasheet']):
                self.verboseOut(Verbosity.HIGH,Severity.WARNING," "*indentation+"missing datasheet, please provide a datasheet link if it isn't a generic component")
                if (documentation['description'] and
                    documentation['keywords']):
                    self.only_datasheet_missing = True

            # counts as violation if only datasheet is missing and verbosity is high
            if self.verbosity and self.verbosity > Verbosity.NORMAL:
                return True

            return not self.only_datasheet_missing

        elif name.lower() in documentation['description'].lower():
            self.verboseOut(Verbosity.HIGH, Severity.WARNING, " "*indentation + "symbol name should not be included in description")
            return True

        else:
            self.verboseOut(Verbosity.HIGH,Severity.SUCCESS," "*indentation+"documentation OK")
            return False


    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.NORMAL, Severity.INFO, "FIX: not supported" )
