# -*- coding: utf-8 -*-

from rules.rule import *
import os

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Rule 10.1', 'Footprint name must match its filename. (.kicad_mod files).')
        
    def check(self):
        """
        Proceeds the checking of the rule.
        """
        
        err = False
        
        module = self.module
        if os.path.splitext(os.path.basename(module.filename))[0] != module.name:
            self.error("footprint name (in file) was '{0}', but expected (from filename) '{1}'.\n".format(module.name, os.path.splitext(os.path.basename(module.filename))[0]))
            err = True
            
        if module.value['value'] != module.name:
            self.error("Value label '{lbl}' does not match filename '{fn}'".format(
                lbl=module.value['value'],
                fn = module.name))
            err = True
            
            
        self.has_illegal_chars = False
        if not isValidName(module.name):
            self.error("Module name '{name}' contains invalid characters as per KLC 1.7".format(
                name = module.name))
            err = True
            self.has_illegal_chars = True
            
        return err

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            self.info("Setting footprint value to '{name}'".format(name = module.name))
            module.name = os.path.splitext(os.path.basename(module.filename))[0]
            module.value['value'] = module.name
