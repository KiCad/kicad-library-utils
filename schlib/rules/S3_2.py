# -*- coding: utf-8 -*-

from rules.rule import *


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Text fields should use common size of 50mils, but labels and numbers may use text size as low as 20mil if required')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * violating_pins
            * violating_fields
        """
        self.violating_fields = []
        for field in self.component.fields:
            text_size = int(field['text_size'])
            if (text_size != 50):
                self.violating_fields.append(field)
                if "reference" in field.keys():
                    message = field["reference"][1:-1]
                elif len(field["name"]) > 2:
                    message = field["name"][1:-1]
                else:
                    message = "UNKNOWN"
                message += (" at posx {0} posy {1}".format(field["posx"], field["posy"]))
                self.error(" - Field {0} size {1}".format(message, field["text_size"]))

        self.violating_pins = []

        """
        Pin number MUST be 50mils
        Pin name must be between 20mils and 50mils
        Pin name should be 50mils
        """

        for pin in self.component.pins:
            name_text_size = int(pin['name_text_size'])
            num_text_size = int(pin['num_text_size'])

            if (name_text_size < 20) or (name_text_size > 50) or (num_text_size < 20) or (num_text_size > 50):
                self.violating_pins.append(pin)
                self.error(' - Pin {0} ({1}), text size {2}, number size {3}'.format(pin['name'], pin['num'], pin['name_text_size'], pin['num_text_size']))
            else:
                if name_text_size != 50:
                    self.warning("Pin name text size should be 50mils (or 20...50mils if required by the symbol geometry)")
                if num_text_size != 50:
                    self.warning("Pin number text size should be 50mils (or 20...50mils if required by the symbol geometry)")

        if (len(self.violating_fields) > 0 or
            len(self.violating_pins) > 0):
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if len(self.violating_fields) > 0:
            self.info("Fixing field text size")
        for field in self.violating_fields:
            field['text_size'] = '50'

        if len(self.violating_pins) > 0:
            self.info("Fixing pin text size")
        for pin in self.violating_pins:
            pin['name_text_size'] = '50'
            pin['num_text_size'] = '50'
        self.recheck()


