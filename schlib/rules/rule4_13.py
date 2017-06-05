# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 4.13 - Power flag symbols', 'Power-flag symbols follow some special rules/KLC-exceptions')
        self.makePinINVISIBLE=False
        self.makePinPowerInput=False
        self.fixTooManyPins=False

    
    def check(self):
        """
        Proceeds the checking of the rule.
        """
        
        fail=False
        if self.component.isPossiblyPowerSymbol():
            if (len(self.component.pins) != 1):
                self.error("Power-flag symbols have exactly one pin")
                fail=True
                self.fixTooManyPins=True
            else:
                if (self.component.pins[0]['electrical_type'].lower() != 'w'):
                    self.error("The pin in power-flag symbols has to be of a POWER-type")
                    fail=True
                    self.makePinPowerInput=True
                if (not self.component.pins[0]['pin_type'].startswith('N')):
                    self.error("The pin in power-flag symbols has to be INVISIBLE")
                    fail=True
                    self.makePinINVISIBLE=True
        
        return fail

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.fixTooManyPins:
            self.info("FIX for too many pins in power-symbol not supported")
        if self.makePinPowerInput:
            self.info("FIX: switching pin-type to power-input")
            self.component.pins[0]['electrical_type']='w'
        if self.makePinINVISIBLE:
            self.info("FIX: making pin invisible")
            self.component.pins[0]['pin_type']='N'+self.component.pins[0]['pin_type']
