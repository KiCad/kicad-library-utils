# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Rule 9.2', 'For through-hole components, footprint anchor is set on pad 1')
        
        self.pin1_position = []
        self.pin1_count = 0

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        module = self.module
        # check if module is through-hole
        if module.attribute == 'pth':
            pads = module.getPadsByNumber(1)
            if len(pads) == 0:
                pads = module.getPadsByNumber('A1')
                
            if len(pads) == 0:
                self.error("Pad 1 not found in footprint")
                return True
                
            self.pin1_count = len(pads)
                
            for pad in pads:
                pos = pad['pos']
                
                if len(self.pin1_position) == 0:
                    self.pin1_position = [pos['x'], pos['y']]
                    
                # Pad is located at origin
                if pos['x'] == 0 and pos['y'] == 0:
                    return False
                    
            self.error("Pad 1 not located at origin")
            self.errorExtra("Set origin to location of Pad 1")
            
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check() and len(self.pin1_position)>0:
            self.info("Moved anchor position to Pin-1")
            module.setAnchor(self.pin1_position)
