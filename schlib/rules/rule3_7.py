# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.7', 'Value field is filled with the component name')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        
        fail = False
        
        value = self.component.fields[1]
        
        name = value['name']
        
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
            
        if not name == self.component.name:
            fail = True
            self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Value {val} does not match component name.".format(val=name))
            
        return fail

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.HIGH, Severity.INFO, "Fixing..")
        self.component.fields[1]['name'] = self.component.name
        
        self.recheck()
