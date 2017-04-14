# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 4.1 - Pin placement', 'Pins must be placed on regular grid, and be of correct length')

    def checkPinOrigin(self):
        self.violating_pins = []
        err = False
        for pin in self.component.pins:
            posx = int(pin['posx'])
            posy = int(pin['posy'])
            if (posx % 100) != 0 or (posy % 100) != 0:
                self.violating_pins.append(pin)
                if not err:
                    self.error("Pins not located on 100mil grid:")
                self.error(' - Pin {0} ({1}), {2}'.format(pin['name'], pin['num'], positionFormater(pin)))
                err = True
    
        return len(self.violating_pins) > 0
    
    def checkPinLength(self):
        self.violating_pins = []
        
        for pin in self.component.pins:
            length = int(pin['length'])
            
            err = False
            
            # ignore zero-length pins e.g. hidden power pins
            if length == 0: continue
            
            if length < 50:
                self.error("{pin} length ({len}mils) is below 50mils".format(pin=pinString(pin), len=length))
            elif length < 100:
                self.warning("{pin} length ({len}mils) is below 100mils".format(pin=pinString(pin), len=length))
            
                
            if length % 50 != 0:
                self.warning("{pin} length ({len}mils) is not a multiple of 50mils".format(pin=pinString(pin), len=length))
                    
            # length too long flags a warning
            if length > 300:
                err = True
                self.error("{pin} length ({length}mils) is longer than maximum (300mils)".format(
                    pin = pinString(pin),
                    length = length))
                    
            if err:
                self.violating_pins.append(pin)

        return len(self.violating_pins) > 0
    
    def check(self):
    
        return any([
            self.checkPinOrigin(),
            self.checkPinLength()
            ])


        return True if len(self.violating_pins) > 0 else False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        
        self.info("Fix not supported")
        
        if self.checkPinOrigin():
            pass
            
        if self.checkPinLength():
            pass