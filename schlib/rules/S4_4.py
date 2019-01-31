# -*- coding: utf-8 -*-

from rules.rule import *
import re


class Rule(KLCRule):

    # Power Input Pins should be 'W'
    POWER_INPUTS = ['^[ad]*g(rou)*nd$', '^[ad]*v(aa|cc|dd|ss|bat|in)$']

    # Power Output Pins should be 'w'
    POWER_OUTPUTS = ['^vout$']

    PASSIVE_PINS = []

    # Input Pins should be "I"
    INPUT_PINS = ['^sdi$', '^cl(oc)*k(in)*$', '^~*cs~*$', '^[av]ref$']

    # Output pins should be "O"
    OUTPUT_PINS = ['^sdo$', '^cl(oc)*kout$']

    # Bidirectional pins should be "B"
    BIDIR_PINS = ['^sda$', '^s*dio$']

    warning_tests = {
        "w": POWER_OUTPUTS,
        "P": PASSIVE_PINS,
        "I": INPUT_PINS,
        "O": OUTPUT_PINS,
        "B": BIDIR_PINS,
        }

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
        super(Rule, self).__init__(component, 'Pin electrical type should match pin function')

    # These pin types must be satisfied
    def checkPowerPins(self, pins):

        self.power_errors = []

        for pin in pins:
            name = pin['name'].lower()
            etype = pin['electrical_type']

            inSpecialStack = False
            Rule43NotExecuted = True
            if hasattr(self.component, 'padInSpecialPowerStack'):
                inSpecialStack = pin['num'] in self.component.padInSpecialPowerStack
                Rule43NotExecuted = False

            if self.test(name.lower(), self.POWER_INPUTS) and (not etype.lower() == 'w') and (not inSpecialStack):
                if len(self.power_errors) == 0:
                    self.error("Power pins should be of type POWER INPUT or POWER OUTPUT")
                    if Rule43NotExecuted:
                        self.errorExtra("NOTE: If power-pins have been stacked, you may ignore this error in some cases (Ensure to check rule S4.3 in addition to recognize such stacks).")
                self.power_errors.append(pin)
                self.errorExtra("{pin} is of type {t}".format(
                    pin=pinString(pin),
                    t=pinElectricalTypeToStr(etype)))

        return len(self.power_errors) > 0

    # These pin types are suggestions
    def checkSuggestions(self, pins):

        self.suggestions = []

        for pin in pins:
            name = pin['name'].lower()
            etype = pin['electrical_type']

            for pin_type in self.warning_tests.keys():
                pins = self.warning_tests[pin_type]

                tests = self.warning_tests[pin_type]

                if self.test(name, tests):

                    if not pin_type == etype:
                        if len(self.suggestions) == 0:
                            self.warning("Pin types should match pin function")
                        self.suggestions.append(pin)
                        self.warningExtra("{pin} is type {t1} : suggested {t2}".format(
                                        pin=pinString(pin),
                                        t1=pinElectricalTypeToStr(etype),
                                        t2=pinElectricalTypeToStr(pin_type)))

                    break

        # No error generated for this rule
        return False

    def checkDoubleInversions(self, pins):

        self.inversion_errors = []

        for pin in pins:
            m = re.search('(\~)(.+)', pin['name'])
            if m and pin['pin_type'] == 'I':
                if len(self.inversion_errors) == 0:
                    self.error("Pins should not be inverted twice (with inversion-symbol on pin and overline on label)")
                self.inversion_errors.append(pin)
                self.errorExtra("{pin} : double inversion (overline + pin type:Inverting)".format(pin=pinString(pin)))

        return len(self.inversion_errors) > 0

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * probably_wrong_pin_types
            * double_inverted_pins
        """

        pins = self.component.pins

        return any([
            self.checkPowerPins(pins),
            self.checkDoubleInversions(pins),
            self.checkSuggestions(pins)
            ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing...")

        for pin in self.power_errors:

            pin['electrical_type'] = 'W'  # Power Input

            self.info("Changing pin {n} type to POWER_INPUT".format(n=pin['num']))

        for pin in self.inversion_errors:
            pin['pin_type'] = ""  # reset pin type (removes dot at the base of pin)
            self.info("Removing double inversion on pin {n}".format(n=pin['num']))

        self.recheck()
