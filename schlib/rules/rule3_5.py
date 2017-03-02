# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):

    #Power Input Pins should be 'W'
    POWER_INPUTS = ['^[ad]*g(rou)*nd$', '^[ad]*v(aa|cc|dd|ss|bat|in)$']

    #Power Output Pins should be 'w'
    POWER_OUTPUTS = ['^vout$']

    PASSIVE_PINS = []

    #Input Pins should be "I"
    INPUT_PINS = ['^sdi$', '^cl(oc)*k(in)*$', '^~*cs~*$', '^[av]ref$']

    #Output pins should be "O"
    OUTPUT_PINS = ['^sdo$', '^cl(oc)*kout$']

    #Bidirectional pins should be "B"
    BIDIR_PINS = ['^sda$', '^s*dio$']

    warning_tests = {
        "w" : POWER_OUTPUTS,
        "P" : PASSIVE_PINS,
        "I" : INPUT_PINS,
        "O" : OUTPUT_PINS,
        "B" : BIDIR_PINS,
        }

    #check if a pin name fits within a list of possible pins (using regex testing)
    def test(self, pinName, nameList):

        for name in nameList:
            if re.search(name,pinName,flags=re.IGNORECASE) is not None:
                return True

        return False

    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, '3.5', 'Pin electrical type should match pin function')

    # These pin types must be satisfied
    def checkPowerPin(self, pin):
    
        err = False
    
        name = pin['name'].lower()
        etype = pin['electrical_type']
        
        # Check power pins (can be either power inputs or outputs)
        if self.test(name.lower(), self.POWER_INPUTS) and not etype.lower() == 'w':
            err = True
            self.power_errors.append(pin)
            self.error("Pin {n} ({name}) should be of type POWER INPUT or POWER OUTPUT".format(
                        n = pin['num'],
                        name = name))
    
    # These pin types are suggestions
    def checkSuggestions(self, pin):
        name = pin['name'].lower()
        etype = pin['electrical_type']
        
        for pin_type in self.warning_tests.keys():
            pins = self.warning_tests[pin_type]
            
            if self.test(name, pins) and not etype == pin_type:
                self.error("Pin {n} ({name}) is type {t1} : suggested {t2}".format(
                            n = pin['num'],
                            name = pin['name'],
                            t1 = pinElectricalTypeToStr(etype),
                            t2 = pinElectricalTypeToStr(pin_type)))
                                    
    def checkDoubleInversion(self, pin):
        
        fail = False
        
        m = re.search('(\~)(.+)', pin['name'])
        
        if m and pin['pin_type'] == 'I':
            fail = True
            self.inversion_errors.append(pin)
            self.error('pin {0} ({1}): double inversion (overline + pin type:Inverting)'.format(pin['name'], pin['num']))

        return fail
        
    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * probably_wrong_pin_types
            * double_inverted_pins
        """
        
        self.power_errors = []
        self.inversion_errors = []

        fail = False
        
        for pin in self.component.pins:
        
            if self.checkPowerPin(pin):
                fail = True
                
            if self.checkDoubleInversion(pin):
                fail = True
                
            self.checkSuggestions(pin)
        
        return fail
        
    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing...")
        
        for pin in self.power_errors:
        
            pin['electrical_type'] = 'W' # Power Input
            
            self.info("Changing pin {n} type to POWER_INPUT".format(n=pin['num']))

        for pin in self.inversion_errors:
            pin['pin_type']="" #reset pin type (removes dot at the base of pin)
            self.info("Removing double inversion on pin {n}".format(n=pin['num']))

        self.recheck()
