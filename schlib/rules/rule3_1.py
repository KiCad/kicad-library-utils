# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.1', 'Pin placement')

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
                self.error(' - pin: {0} ({1}), {2}'.format(pin['name'], pin['num'], positionFormater(pin)))
                err = True
    
        return len(self.violating_pins) > 0
    
    def checkPinLength(self):
        self.violating_pins = []
        err = False
        for pin in self.component.pins:
            length = int(pin['length'])
            
            # ignore zero-length pins e.g. hidden power pins
            if length == 0: continue
            
            if length < 100 or length % 50 != 0:
                self.violating_pins.append(pin)
                if not err:
                    self.error("Incorrect pin length:")
                self.error(' - pin: {0} ({1}), {2}, length={3}'.format(pin['name'], pin['num'], positionFormater(pin), length))
                err = True

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