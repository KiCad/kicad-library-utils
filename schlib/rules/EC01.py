# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):

    #Power Input Pins should be 'W'
    POWER_INPUTS = ['^[ad]*g(rou)*nd$', '^[ad]*v(aa|cc|dd|ss|bat|in)$', '^[av]ref$']
    
    #Power Output Pins should be 'w'
    POWER_OUTPUTS = ['^vout$']
    
    PASSIVE_PINS = []
    
    #Input Pins should be "I"
    INPUT_PINS = ['^sdi$', '^cl(oc)*k(in)*$', '^~*cs~*$',]
    
    #Output pins should be "O"
    OUTPUT_PINS = ['^sdo$', '^cl(oc)*kout$']
    
    #Bidirectional pins should be "B"
    BIDIR_PINS = ['^sda$', '^s*dio$']
    
    #No-connect pins should be "N"
    NC_PINS = ['^nc$', '^dnc$', '^n\.c\.$']
    
    tests = {
        "W" : POWER_INPUTS,
        "w" : POWER_OUTPUTS,
        "P" : PASSIVE_PINS,
        "I" : INPUT_PINS,
        "O" : OUTPUT_PINS,
        "B" : BIDIR_PINS,
        "N" : NC_PINS,
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
        super(Rule, self).__init__(component, 'EC01 - Extra Checking', 'Check pins names against pin types.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * probably_wrong_pin_types
            * double_inverted_pins
        """
        fail = False
        
        self.probably_wrong_pin_types = []
        self.double_inverted_pins = []
        
        for pin in self.component.pins:
            
            name = pin['name'].lower()
            etype = pin['electrical_type']
            
            #Check that the pin names match the (best guess) pin types
            for pin_type in self.tests.keys():
                pins = self.tests[pin_type]
                
                if self.test(name, pins) and not etype == pin_type:
                    fail = True
                    self.probably_wrong_pin_types.append(pin)
                    
                    self.verboseOut(Verbosity.HIGH,Severity.WARNING,'pin {0} ({1}): {2} ({3}), expected: {4} ({5})'.format(
                        pin['name'],
                        pin['num'],
                        pin['electrical_type'],
                        pinElectricalTypeToStr(pin['electrical_type']),
                        pin_type,
                        pinElectricalTypeToStr(pin_type)))
            
            # check if name contains overlining
            m = re.search('(\~)(.+)', pin['name'])
            if m and pin['pin_type'] == 'I':
                fail = True
                self.double_inverted_pins.append(pin)
                self.verboseOut(Verbosity.HIGH,Severity.WARNING,'pin {0} ({1}): double inversion (overline + pin type:Inverting)'.format(pin['name'], pin['num']))

            # check if pin names are empty
            if len(pin['name']) == 0 or pin['name'] == '~':
                fail = True
                self.verboseOut(Verbosity.HIGH, Severity.WARNING, "pin {n} does not have a name".format(n=pin['num']))
                
            # check if NC pins are visible
            if pin['electrical_type'] == 'N':
                if not pin['pin_type'].startswith('N'):
                    fail = True
                    self.verboseOut(Verbosity.HIGH, Severity.WARNING, "pin {name} ({n}) is no-connect, should be set to invisible".format(n=pin['num'],name=pin['name']))
                
        return fail
        
    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.HIGH, Severity.INFO,"Fixing...")
        for pin in self.probably_wrong_pin_types:
        
            for pin_type in self.tests.keys():
                pin_names = self.tests[pin_type]
                
                #we have found the 'correct' pin type...
                if self.test(pin['name'],pin_names):
                    self.verboseOut(Verbosity.HIGH, Severity.WARNING, 'changing pin {0} ({1} - {2}) to ({3} - {4})'.format(
                        pin['name'],
                        pin['electrical_type'],
                        pinElectricalTypeToStr(pin['electrical_type']),
                        pin_type,
                        pinElectricalTypeToStr(pin_type)))
                    
                    pin['electrical_type'] = pin_type

        for pin in self.double_inverted_pins:
            pin['pin_type']="" #reset pin type (removes dot at the base of pin)

        self.recheck()
