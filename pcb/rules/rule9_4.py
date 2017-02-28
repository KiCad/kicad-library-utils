# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Rule 9.4', 'THT pad layer requirements')
        
        self.required_layers = ["*.Cu","*.Mask"]
        
    def checkPad(self, pad):
        layers = pad['layers']
        
        # For THT parts, following layers required:
        # *.Cu
        # F.mask
        # B.mask
        
        if not pad['type'] == 'thru_hole':
            return False
        
        err = False
        
        # check required layers
        for layer in self.required_layers:
            if layer not in layers:
                self.addMessage("Pad '{n}' missing layer '{lyr}'".format(
                    n=pad['number'],
                    lyr=layer))
                err = True
                    
        # check for extra layers
        for layer in layers:
            if layer not in self.required_layers:
                self.addMessage("Pad '{n}' has extra layer '{lyr}'".format(
                    n=pad['number'],
                    lyr=layer))
                err = True
                
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
        module = self.module
        
        for pad in module.filterPads('thru_hole'):
            pad['layers'] = self.required_layers
        
