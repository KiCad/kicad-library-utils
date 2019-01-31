# -*- coding: utf-8 -*-

from rules.rule import *


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Part meta-data is filled in as appropriate')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * only_datasheet_missing
        """

        self.only_datasheet_missing = False
        invalid_documentation = 0

        # check part itself
        if self.checkDocumentation(self.component.name, self.component.documentation, False, self.component.isGraphicSymbol() or self.component.isPowerSymbol()):
            invalid_documentation += 1

        # check all its aliases too
        if self.component.aliases:
            invalid = []
            for alias in self.component.aliases.keys():
                if self.checkDocumentation(alias, self.component.aliases[alias], True, self.component.isGraphicSymbol() or self.component.isPowerSymbol()):
                    invalid_documentation += 1

        return invalid_documentation > 0

    def checkDocumentation(self, name, documentation, alias=False, isGraphicOrPowerSymbol=False):

        errors = []
        warnings = []

        if not documentation:
            errors.append("Missing all fields on 'Properties > Description' tab")
        elif (not documentation['description'] or
            not documentation['keywords'] or
            not documentation['datasheet']):

            if (not documentation['description']):
                errors.append("Missing DESCRIPTION field on 'Properties > Description' tab")
            if (not documentation['keywords']):
                errors.append("Missing KEYWORDS field on 'Properties > Description' tab")
            if (not isGraphicOrPowerSymbol) and (not documentation['datasheet']):
                errors.append("Missing DOCUMENTATION FILE NAME field on 'Properties > Description' tab")

                if (documentation['description'] and
                    documentation['keywords']):
                    self.only_datasheet_missing = True

        # Symbol name should not appear in the description
        desc = documentation.get('description', '')
        if desc and name.lower() in desc.lower():
            warnings.append("Symbol name should not be included in description")

        # Datasheet field should look like a a datasheet
        ds = documentation.get('datasheet', '')

        if ds and len(ds) > 2:
            link = False
            links = ['http', 'www', 'ftp']
            if any([ds.startswith(i) for i in links]):
                link = True
            elif ds.endswith('.pdf') or '.htm' in ds:
                link = True

            if not link:
                warnings.append("Datasheet entry '{ds}' does not look like a URL".format(ds=ds))

        if len(errors) > 0 or len(warnings) > 0:
            msg = "{cmp} {name} has metadata errors:".format(
                cmp="ALIAS" if alias else "Component",
                name=name)
            if len(errors) == 0:
                self.warning(msg)
            else:
                self.error(msg)

            for err in errors:
                self.errorExtra(err)
            for warn in warnings:
                self.warningExtra(warn)

        return len(errors) > 0

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("FIX: not supported")
