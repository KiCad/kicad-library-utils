# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Rule 9.5', 'Minimum drill size')
        
    def checkPad(self, pad):
        
        drill = pad['drill']
        size = min(drill['size']['x'], drill['size']['y'])
        
        err = False
        
        if size < 0.15:
            self.error("Pad {n} min. drill size ({d}mm) is below minimum (0.15mm)".format(
                n = pad['number'],
                d = size))
            err = True
        elif size < 0.20:
            self.warning("Pad {n} min. drill size ({d}mm) is below recommended (0.20mm)".format(
                n = pad['number'],
                d = size))
                
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
        self.info("Fix - not supported for this rule")
       