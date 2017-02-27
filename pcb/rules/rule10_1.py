# -*- coding: utf-8 -*-

from rules.rule import *
import os

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 10.1', 'Footprint name must match its filename')

        self.illegal_chars = ['*', '?', ':', '/', '\\', '[', ']', ';', '|', '=', ',']
        
    def check(self):
        """
        Proceeds the checking of the rule.
        """
        
        err = False
        
        module = self.module
        if os.path.splitext(os.path.basename(module.filename))[0] != module.name:
            self.addMessage("footprint name (in file) was '{0}', but expected (from filename) '{1}'.\n".format(module.name, os.path.splitext(os.path.basename(module.filename))[0]))
            err = True
            
        if module.value['value'] != module.name:
            self.addMessage("Contents of values label ({lbl}) do not match filename".format(lbl=module.value))
            err = True
            
        for c in self.illegal_chars:
            if c in module.name:
                self.addMessage("Illegal character in filename: {c}".format(c=c))
                err = True
            
        return Err

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.name = os.path.splitext(os.path.basename(module.filename))[0]
            module.value['value'] = module.name