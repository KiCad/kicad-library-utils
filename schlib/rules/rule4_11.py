# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 4.11 - Default footprint', 'For components with a single default footprint, footprint field is filled with valid footprint filename')

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        
        fail = False

        # Footprint field is index [2]
        if len(self.component.fields) >= 3:
            fp = self.component.fields[2]
            fp_name = fp['name']
            
            # Strip the quote characters
            if fp_name.startswith('"') and fp_name.endswith('"'):
                fp_name = fp_name[1:-1]
            
            fp_desc = "Footprint field '{fp}' ".format(fp=fp_name)
            
            # Only check if there is text in the name
            if len(fp_name) > 0:
                #footprint field should be set to invisible (if it has any text in it)
                if fp['visibility'] == 'V':
                    fail = True
                    self.error(fp_desc + "should be set to invisible.")
                   
                # Footprint field should be of the format "Footprint_Library:Footprint_Name"
                if fp_name.count(":") is not 1 or fp_name.startswith(":") or fp_name.endswith(":"):
                    fail = True
                    self.error(fp_desc + "should be of the format 'Library:Footprint'")
                    
                # Footprint name cannot contain any illegal pathname characters
                invalid = '\/*?"<>|[]\'@#~`'
                for ii in invalid:
                    if ii in fp_name:
                        self.error(fp_desc + " contains illegal character '{c}'".format(c=ii))
            
        return fail

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("FIX: not supported")
