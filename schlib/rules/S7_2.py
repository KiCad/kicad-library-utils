# -*- coding: utf-8 -*-

from rules.rule import *
import re


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Graphical symbols follow some special rules/KLC-exceptions')
        self.fixTooManyPins = False
        self.fixNoFootprint = False

    def check(self):
        """
        Proceeds the checking of the rule.
        """

        fail = False
        if self.component.isGraphicSymbol():
            # no pins in raphical symbol
            if (len(self.component.pins) != 0):
                self.error("Graphical symbols have no pins")
                fail = True
                self.fixTooManyPins = True
            # footprint field must be empty
            if self.component.fields[2]['name'] != '' and self.component.fields[2]['name'] != '""':
                self.error("Graphical symbols have no footprint association (footprint was set to '"+self.component.fields[2]['name']+"')")
                fail = True
                self.fixNoFootprint = True
            # FPFilters must be empty
            if len(self.component.fplist) > 0:
                self.error("Graphical symbols have no footprint filters")
                fail = True
                self.fixNoFootprint = True

        return fail

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.fixTooManyPins:
            self.info("FIX for too many pins in graphical symbol not supported")
        if self.fixNoFootprint:
            self.info("FIX empty footprint association and FPFilters")
            self.component.fplist.clear()
            self.component.fields[2] = ''
