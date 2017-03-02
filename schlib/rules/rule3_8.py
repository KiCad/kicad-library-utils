# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.8', 'Default fields contain the correct information')
        
    def checkVisibility(self, field):
        return field['visibility'] == 'V'
        
    def checkReference(self):
        
        fail = False
        
        ref = self.component.fields[0]
        
        if not self.checkVisibility(ref):
            self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Ref field must be VISIBLE")
            fail = True
    
        return fail
        
    def checkValue(self):
        fail = False
        
        value = self.component.fields[1]
        
        name = value['name']
        
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
            
        if not name == self.component.name:
            fail = True
            self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Value {val} does not match component name.".format(val=name))
            
        # name field must be visible!
        if not self.checkVisibility(value):
            self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Value field must be VISIBLE")
            fail = True
                
        return fail
    
    def checkFootprint(self):
        # Footprint field must be invisible
        fail = False
        
        fp = self.component.fields[2]
        
        if self.checkVisibility(fp):
            self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Footprint field must be INVISIBLE")
            fail = True
        
        return fail
    
    def checkDatasheet(self):
        
        # Datasheet field must be invisible
        fail = False
        
        ds = self.component.fields[3]
        
        if self.checkVisibility(ds):
            self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Datasheet field must be INVISIBLE")
            fail = True
            
        return fail
        
    def check(self):
    
    
        # Check for required fields
        n = len(self.component.fields)
        if n < 4:
            self.verboseOut(Verbosity.HIGH,
                            Severity.ERROR,
                            "Component does not have minimum required fields!")
                            
            if n < 1:
                self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Missing REFERENCE field")
                            
            if n < 2:
                self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Missing VALUE field")
                            
            if n < 3:
                self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Missing FOOTPRINT field")
                            
            if n < 4:
                self.verboseOut(Verbosity.HIGH, Severity.ERROR, "Missing DATASHEET field")
                            
            return True
    
        return any([
            self.checkReference(),
            self.checkValue(),
            self.checkFootprint(),
            self.checkDatasheet()
            ])
        
        

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.HIGH, Severity.INFO, "Fixing..")
        self.component.fields[1]['name'] = self.component.name
        
        self.recheck()
