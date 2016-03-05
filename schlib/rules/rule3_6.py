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
        """
        self.violating_fields = []
        for field in self.component.fields:
            text_size = int(field['text_size'])
            if (text_size != 50):
                self.violating_fields.append(field)
                keys=field.keys()
                message=""
                if("reference" in keys):
                    message+=field["reference"]
                else:
                    message+=field["name"]
                self.verboseOut(Verbosity.HIGH, Severity.ERROR,"field: "+message+" size"+field["text_size"])


        self.violating_pins = []
        for pin in self.component.pins:
            name_text_size = int(pin['name_text_size'])
            num_text_size = int(pin['num_text_size'])
            if (name_text_size != 50) or (num_text_size != 50):
                self.violating_pins.append(pin)
                self.verboseOut(Verbosity.HIGH, Severity.ERROR, 'pin: %s (%s), text size %s, number size %s' %
                           (pin['name'], pin['num'], pin['name_text_size'], pin['num_text_size']))

        if (len(self.violating_fields) > 0 or
            len(self.violating_pins) > 0):
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.HIGH, Severity.INFO,"Fixing...")
        for field in self.violating_fields:
            field['text_size'] = '50'

        for pin in self.violating_pins:
            pin['name_text_size'] = '50'
            pin['num_text_size'] = '50'
        if self.check():
            self.verboseOut(Verbosity.HIGH, Severity.ERROR,"...could't be fixed")
        else:
            self.verboseOut(Verbosity.HIGH, Severity.SUCCESS,"everything fixed")


