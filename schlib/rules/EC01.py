# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC01 - Extra Checking',
                                   'Check pins names against pin types.')

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

            # check if name contains overlining
            m = re.search('(\~)(.*)(\~)', pin['name'])
            if m and pin['pin_type'] == 'I':
                self.probably_wrong_pin_types.append(pin)

        return False if len(self.probably_wrong_pin_types) == 0 else True

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check():
            for pin in self.probably_wrong_pin_types:
                pin['electrical_type'] = 'W'
