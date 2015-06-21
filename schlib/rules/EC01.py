# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC01 - Extra Checking', 'Check if pins named *GND*, *VCC* or *VDD* have power input pin type.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * probably_wrong_pin_types
        """
        self.probably_wrong_pin_types = []
        for pin in self.component.pins:
            if ('GND' in pin['name'].upper() or
                'VCC' in pin['name'].upper() or
                'VDD' in pin['name'].upper()):
                if pin['electrical_type'] != 'W':
                    self.probably_wrong_pin_types.append(pin)
        return False if len(self.probably_wrong_pin_types) == 0 else True

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check():
            for pin in self.probably_wrong_pin_types:
                pin['electrical_type'] = 'W'
