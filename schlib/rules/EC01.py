# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC01 - Extra checking', 'General pin checking')

    def checkPinNames(self):
        self.wrong_pin_numbers = []
        for pin in self.component.pins:
            try:
                num = int(pin['num'])
            except ValueError:
                # BGA pins checking
                m = re.search('([A-z]*)([0-9]*)', pin['num'])

                # if group 2 is empty there are only letters in the pin name
                if m.group(2) == '':
                    self.wrong_pin_numbers.append(pin)
                    self.error("pin: {0} number {1} is not valid, should contain at least 1 number".format(pin['name'], pin['num']))

                    
        return len(self.wrong_pin_numbers) > 0
        
    def checkDuplicatePins(self):
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
                self.error("Pin {n} is duplicated".format(n=number))

                for pin in pin_list:
                    self.error("{n} - {name} @ {x},{y}".format(
                        n = pin['num'],
                        name = pin['name'],
                        x = pin['posx'],
                        y = pin['posy']))

        return duplicate
        
        
    # Check pin numbers only generates a warning
    def checkPinNumbers(self):
        #check for missing pins within the range of pins
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
        self.info("FIX: not supported" )
