# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.6', 'Field text uses a common size of 50mils.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * violating_pins
            * violating_fields
            * violating_texts
        """
        self.violating_fields = []
        for field in self.component.fields:
            text_size = int(field['text_size'])
            if (text_size != 50):
                self.violating_fields.append(field)

        self.violating_texts = []
        for text in self.component.draw['texts']:
            text_size = int(text['text_size'])
            if text_size != 50:
                self.violating_texts.append(text)

        self.violating_pins = []
        for pin in self.component.pins:
            name_text_size = int(pin['name_text_size'])
            num_text_size = int(pin['num_text_size'])
            if (name_text_size != 50) or (num_text_size != 50):
                self.violating_pins.append(pin)

        if (len(self.violating_fields) > 0 or
            len(self.violating_texts) > 0 or
            len(self.violating_pins) > 0):
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check():
            for field in self.violating_fields:
                field['text_size'] = '50'

            for text in self.violating_texts:
                text['text_size'] = '50'

            for pin in self.violating_pins:
                pin['name_text_size'] = '50'
                pin['num_text_size'] = '50'
