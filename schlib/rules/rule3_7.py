# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.7', 'Field text uses a common size of 50mils.')

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
                if("reference" in field.keys()):
                    message=field["reference"][1:-1]
                elif (len(field["name"])>2):
                    message=field["name"][1:-1]
                else:
                    message="UNKNOWN"
                message+=(" at posx {0} posy {1}".format(field["posx"],field["posy"]))
                self.error("field: {0} size {1}".format(message,field["text_size"]) )


        self.violating_pins = []
        for pin in self.component.pins:
            name_text_size = int(pin['name_text_size'])
            num_text_size = int(pin['num_text_size'])
            if (name_text_size != 50) or (num_text_size != 50):
                self.violating_pins.append(pin)
                self.error('pin: {0} ({1}), text size {2}, number size {3}'.format(pin['name'], pin['num'], pin['name_text_size'], pin['num_text_size']))

        if (len(self.violating_fields) > 0 or
            len(self.violating_pins) > 0):
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing...")
        for field in self.violating_fields:
            field['text_size'] = '50'

        for pin in self.violating_pins:
            pin['name_text_size'] = '50'
            pin['num_text_size'] = '50'
        self.recheck()


