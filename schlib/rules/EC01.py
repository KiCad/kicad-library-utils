# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):

    #Power Input Pins should be 'W'
    POWER_INPUTS = ['gnd','vcc','vdd','ground','vbat','vss','vaa','vin','vi']
    
    #Power Output Pins should be 'w'
    POWER_OUTPUTS = []
    
    PASSIVE_PINS = []
    
    #Input Pins should be "I"
    INPUT_PINS = ['sdi','clk','clock','~cs','cs']
    
    #Output pins should be "O"
    OUTPUT_PINS = ['sdo',]
    
    #Bidirectional pins should be "B"
    BIDIR_PINS = ['sda',]
    
    tests = {
        "W" : POWER_INPUTS,
        "w" : POWER_OUTPUTS,
        "P" : PASSIVE_PINS,
        "I" : INPUT_PINS,
        "O" : OUTPUT_PINS,
        "B" : BIDIR_PINS,
        }

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
        
        self.probably_wrong_pin_types = []
        self.double_inverted_pins = []
        
        for pin in self.component.pins:
            
            name = pin['name'].lower()
            etype = pin['electrical_type']
            
            #run each test
            for pin_type in self.tests.keys():
                pins = self.tests[pin_type]
                
                if any([p in name for p in pins]) and not etype == pin_type:
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
                self.double_inverted_pins.append(pin)
                self.verboseOut(Verbosity.HIGH,Severity.WARNING,'pin {0} ({1}): double inversion (overline + pin type:Inverting)'.format(pin['name'], pin['num']))

        return False if len(self.probably_wrong_pin_types)+len(self.double_inverted_pins) == 0 else True

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.HIGH, Severity.INFO,"Fixing...")
        for pin in self.probably_wrong_pin_types:
        
            for pin_type in self.tests.keys():
                pin_names = self.tests[pin_type]
                
                #we have found the 'correct' pin type...
                if pin['name'].lower() in pin_names:
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
