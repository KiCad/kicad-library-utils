# -*- coding: utf-8 -*-

from rules.rule import *
import re


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Pins should be arranged by function')

    def checkGroundPins(self):

        # Includes negative power pins
        GND = ['^[ad]*g(rou)*nd$', '^[ad]*v(ss)$']

        first = True

        for pin in self.component.pins:
            name = str(pin['name'].lower())
            for gnd in GND:
                if re.search(gnd, name, flags=re.IGNORECASE) is not None:
                    # Pin orientation should be "up"
                    if (not self.component.isPowerSymbol()) and (not pin['direction'] == 'U'):
                        if first:
                            first = False
                            self.warning("Ground and negative power pins should be placed at bottom of symbol")
                        self.warningExtra(pinString(pin))

    def checkPowerPins(self):

        # Positive power pins only
        PWR = ['^[ad]*v(aa|cc|dd|bat|in)$']

        first = True

        for pin in self.component.pins:
            name = str(pin['name'].lower())
            for pwr in PWR:
                if re.search(pwr, name, flags=re.IGNORECASE) is not None:
                    # Pin orientation should be "down"
                    if (not self.component.isPowerSymbol()) and not pin['direction'] == 'D':
                        if first:
                            first = False
                            self.warning("Positive power pins should be placed at top of symbol")
                        self.warningExtra(pinString(pin))

    def check(self):

        self.checkGroundPins()
        self.checkPowerPins()

        # No errors, only warnings
        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing not supported")
