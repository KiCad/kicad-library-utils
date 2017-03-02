# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.10', 'Part meta-data is filled out as appropriate')

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
                self.info("checking alias: {0}".format(alias))
                if self.checkDocumentation(alias, self.component.aliases[alias], indentation=2):
                    invalid_documentation+=1

        return True if invalid_documentation>0 else False


    def checkDocumentation(self, name, documentation, indentation=0):
        if not documentation:
            self.error(" "*indentation+"missing whole documentation (description, keywords, datasheet)")
            return True

        elif (not documentation['description'] or
            not documentation['keywords'] or
            not documentation['datasheet']):

            if (not documentation['description']):
                self.error(" "*indentation+"missing description")
            if (not documentation['keywords']):
                self.error(" "*indentation+"missing keywords")
            if (not documentation['datasheet']):
                self.warning(" "*indentation+"missing datasheet, please provide a datasheet link if it isn't a generic component")
                if (documentation['description'] and
                    documentation['keywords']):
                    self.only_datasheet_missing = True

            # counts as violation if only datasheet is missing and verbosity is high
            if self.verbosity and self.verbosity > Verbosity.NORMAL:
                return True

            return not self.only_datasheet_missing

        elif name.lower() in documentation['description'].lower():
            self.warning( " "*indentation + "symbol name should not be included in description")
            return True

        return False


    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("FIX: not supported" )
