# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 10.2', 'Footprint metadata')

    def checkDocs(self):
        mod = self.module
        error = False
        if not mod.description:
            self.addMessage("Description field is empty")
            return True
            
        return error
        
    def checkTags(self):
        mod = self.module
        error = False    
        if not mod.tags:
            self.addMessage("No keyword tags")
            return True
        
        illegal = [',', ';', ':']
        
        #check for illegal tags
        for char in illegal:
            if char in mod.tags:
                self.addMessage("Tags contain illegal character: ('{c}')".format(c=char))
                error = True
                
        return error
    
    def check(self):
        return any([
            self.checkDocs(),
            self.checkTags()
            ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            # Can't fix this one!
            pass
