# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.2', 'For black-box symbols, pins have a length of 100mils. Large pin numbers can be accomodated by incrementing the width in steps of 50mil.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * violating_pins
        """
        self.violating_pins = []
        for pin in self.component.pins:
            length = int(pin['length'])
            if length == 0: continue
            if (length < 100) or (length % 50 != 0):
                self.violating_pins.append(pin)

        return True if len(self.violating_pins) > 0 else False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check():
            pass
            # TODO
