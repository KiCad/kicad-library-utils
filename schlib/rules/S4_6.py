# -*- coding: utf-8 -*-

from rules.rule import *
import re


class Rule(KLCRule):

    # No-connect pins should be "N"
    NC_PINS = ['^nc$', '^dnc$', '^n\.c\.$']

    # check if a pin name fits within a list of possible pins (using regex testing)
    def test(self, pinName, nameList):

        for name in nameList:
            if re.search(name, pinName, flags=re.IGNORECASE) is not None:
                return True

        return False

    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Unused pins should be set as NOT CONNECTED and should be INVISIBLE')

    def checkNCPins(self, pins):

        self.invisible_errors = []
        self.type_errors = []

        for pin in pins:

            name = pin['name'].lower()
            etype = pin['electrical_type']

            visible = not (pin['pin_type'].startswith('N'))

            # Check NC pins
            if self.test(name.lower(), self.NC_PINS) or etype == 'N':

                # NC pins should be of type N
                if not etype == 'N':  # Not set to NC
                    self.type_errors.append(pin)

                # NC pins should be invisible
                if visible:
                    self.invisible_errors.append(pin)

        if len(self.type_errors) > 0:
            self.error("NC pins are not correct pin-type:")

            for pin in self.type_errors:
                self.errorExtra("{pin} should be of type NOT CONNECTED, but is of type {pintype}".format(
                    pin=pinString(pin),
                    pintype=pinElectricalTypeToStr(pin['electrical_type'])))

        if len(self.invisible_errors) > 0:
            self.warning("NC pins are VISIBLE (should be INVISIBLE):")

            for pin in self.invisible_errors:
                self.warningExtra("{pin} should be INVISIBLE".format(pin=pinString(pin)))

        return len(self.invisible_errors) > 0 or len(self.type_errors) > 0

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * probably_wrong_pin_types
            * double_inverted_pins
        """

        fail = False

        if self.checkNCPins(self.component.pins):
            fail = True

        return fail

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing...")

        for pin in self.invisible_errors:
            if not pin['pin_type'].startswith("N"):
                pin['pin_type'] = 'N' + pin['pin_type']
                self.info("Setting pin {n} to INVISIBLE".format(n=pin['num']))

        for pin in self.type_errors:
            if not pin['electrical_type'] == 'N':
                pin['electrical_type'] = 'N'
                self.info("Changing pin {n} type to NO_CONNECT".format(n=pin['num']))

        self.recheck()
