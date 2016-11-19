# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC05 - Extra Checking', 'Pin numbers should not be duplicated, and all pins should be present')

    def check(self):
        """
        Proceeds the checking of the rule.
        Determines if any symbol pins are duplicated
        """

        #dict of pins
        pins = {}

        #look for duplicate pins
        for pin in self.component.pins:

            pin_number = pin['num']
            pin_name = pin['name']

            #Check if there is already a match for this pin number
            if pin_number in pins.keys():
                pins[pin_number].append(pin)
            else:
                pins[pin_number] = [pin]

        duplicate = False

        for number in pins.keys():
            pin_list = pins[number]

            if len(pin_list) > 1:
                duplicate = True
                self.verboseOut(Verbosity.NORMAL, Severity.WARNING, "Pin {n} is duplicated".format(n=number))

                for pin in pin_list:
                    self.verboseOut(Verbosity.HIGH, Severity.WARNING, "{n} - {name} @ {x},{y}".format(
                        n = pin['num'],
                        name = pin['name'],
                        x = pin['posx'],
                        y = pin['posy']))

        # convert pins numbers to integers
        int_pins = []
        for pin in pins.keys():
            try:
                int_pins.append(int(pin))
            except ValueError:
                return duplicate

        if not int_pins:
            return duplicate

        #check for missing pins within the range of pins
        missing = False
        for i in range(1, max(int_pins) + 1):
            if i not in int_pins:
                self.verboseOut(Verbosity.NORMAL, Severity.WARNING, "Pin {n} is missing".format(n=i))
                missing = True

        return duplicate or missing

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.NORMAL, Severity.INFO, "FIX: not supported" )
