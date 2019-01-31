# -*- coding: utf-8 -*-

from rules.rule import *
import re


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'General pin number checking')

    def checkPinNames(self):
        self.wrong_pin_numbers = []
        for pin in self.component.pins:
            try:
                num = int(pin['num'])
            except ValueError:
                nums = map(str, range(10))

                if not any([num in pin['num'] for num in nums]):
                    self.wrong_pin_numbers.append(pin)
                    self.error("pin: {0} number {1} is not valid, should contain at least 1 number".format(pin['name'], pin['num']))

        return len(self.wrong_pin_numbers) > 0

    def checkDuplicatePins(self):
        # List of lists of pins
        pin_lists = []

        # look for duplicate pin numbers
        # For a pin to be considered a duplicate, it must have:
        # - The same number
        # - Be in the same unit
        # - Be in the same "convert"

        keys = ['num', 'unit', 'convert']

        for pin in self.component.pins:

            found = False

            for i, pin_list in enumerate(pin_lists):

                # Compare against first item
                p_test = pin_list[0]

                # Test each key
                if all([pin[k] == p_test[k] for k in keys]):
                    found = True
                    pin_lists[i].append(pin)
                    break

            if not found:
                pin_lists.append([pin])

        duplicate = False

        for pin_list in pin_lists:
            # Look for duplicate groups
            if len(pin_list) > 1:
                duplicate = True
                self.error("Pin {n} is duplicated:".format(n=pin_list[0]['num']))

                for pin in pin_list:
                    self.errorExtra(pinString(pin))

        return duplicate

    # Check pin numbers only generates a warning
    def checkPinNumbers(self):
        # check for missing pins within the range of pins
        missing = False

        int_pins = []
        for pin in self.component.pins:
            try:
                int_pins.append(int(pin['num']))
            except:
                pass

        for i in range(1, max(int_pins) + 1):
            if i not in int_pins:
                self.warning("Pin {n} is missing".format(n=i))
                missing = True

        return missing

    def check(self):

        return any([
            self.checkPinNames(),
            self.checkDuplicatePins()
            ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("FIX: not supported")
