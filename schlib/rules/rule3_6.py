# -*- coding: utf-8 -*-

from rules.rule import *
import re

class Rule(KLCRule):

    #No-connect pins should be "N"
    NC_PINS = ['^nc$', '^dnc$', '^n\.c\.$']


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
        super(Rule, self).__init__(component, '3.6', 'NC pin checking')
            
    def checkNCPin(self, pin):
        
        err = False
    
        name = pin['name'].lower()
        etype = pin['electrical_type']
        
        # Check NC pins
        if self.test(name.lower(), self.NC_PINS) or etype == 'N':
        
            # NC pins should be of type N
            if not etype == 'N': # Not set to NC
                err = True
                self.error("Pin {n} ({name}) should be of type NOT CONNECTED".format(
                            n = pin['num'],
                            name = name))
                                
            # NC pins should be invisible
            if not pin['pin_type'] == 'I':
                err = True
                self.error("Pin {n} ({name}) is NC and should be INVISIBLE".format(
                            n = pin['num'],
                            name = name))
                            
        if err:
            self.nc_errors.append(pin)
            
        return err
        
    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * probably_wrong_pin_types
            * double_inverted_pins
        """
        
        self.nc_errors = []
        
        fail = False
        
        for pin in self.component.pins:
                
            if self.checkNCPin(pin):
                fail = True
        
        return fail
        
    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing...")
        
        for pin in self.nc_errors:
            if not pin['electrical_type'] == 'N':
                pin['electrical_type'] = 'N'
                self.info("Changing pin {n} type to NO_CONNECT".format(n=pin['num']))
            
            if not pin['pin_type'] == 'I':
                pin['pin_type'] = 'I'
                self.info("Setting pin {n} to INVISIBLE".format(n=pin['num']))

        self.recheck()
