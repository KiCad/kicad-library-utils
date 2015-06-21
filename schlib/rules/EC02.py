# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC02 - Extra Checking', 'Check if pins numbers is indeed a number.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * wrong_pin_numbers
        """
        self.wrong_pin_numbers = []
        for pin in self.component.pins:
            try:
                num = int(pin['num'])
            except ValueError:
                # BGA pins checking
                m = re.search('([A-z]*)([0-9]*)', pin['num'])

                # if group 2 is empty there are only letters in the pin name
                if m.group(2) == '':
                    self.wrong_pin_numbers.append(pin)

        return False if len(self.wrong_pin_numbers) == 0 else True

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check():
            pass
