# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Rule 9.6', 'Minimum annular ring')
        
        self.required_layers = ["*.Cu","*.Mask"]
        
    def checkPad(self, pad):
        
        drill_size = pad['drill']['size']
        drill_x = drill_size['x']
        drill_y = drill_size['y']
        
        pad_size = pad['size']
        pad_x = pad_size['x']
        pad_y = pad_size['y']

        err = False
        
        # Circular pad
        if drill_x == drill_y and pad_x == pad_y:
            ring = (pad_x - drill_x) / 2
            
            if ring < 0.05:
                self.addMessage("Pad {n} annular ring ({d}mm) is below minimum (0.05mm)".format(
                    n = pad['number'],
                    d = ring))
                err = True
                
            elif ring < 0.15:
                self.addMessage("Pad {n} annular ring ({d}mm) is below recommended (0.15mm)".format(
                    n = pad['number'],
                    d = ring))
            
        # Non circular pad
        else:
            ring_x = (pad_x - drill_x) / 2
            
            if ring_x < 0.05:
                self.addMessage("Pad {n} x-dimension annular ring ({d}mm) is below minimum (0.05mm)".format(
                    n = pad['number'],
                    d = ring_x))
                err = True
                
            elif ring_x < 0.15:
                self.addMessage("Pad {n} x-dimension annular ring ({d}mm) is below recommended (0.15mm)".format(
                    n = pad['number'],
                    d = ring_x))
                    
            ring_y = (pad_y - drill_y) / 2
            
            if ring_y < 0.05:
                self.addMessage("Pad {n} y-dimension annular ring ({d}mm) is below minimum (0.05mm)".format(
                    n = pad['number'],
                    d = ring_y))
                err = True
                
            elif ring_y < 0.15:
                self.addMessage("Pad {n} y-dimension annular ring ({d}mm) is below recommended (0.15mm)".format(
                    n = pad['number'],
                    d = ring_y))
                
        return err        
        
    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        module = self.module
        
        return any([self.checkPad(pad) for pad in module.filterPads('thru_hole')])
        
    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        pass
        
