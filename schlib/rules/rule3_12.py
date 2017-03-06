# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.12 - Footprint filters', 'Footprint filters should match all appropriate footprints')

    def checkFilters(self, filters):
    
        self.bad_filters = []
   
        for filter in filters:
            errors = []
            # Filter must contain a "*" wildcard
            if not '*' in filter:
                errors.append("Does not contain wildcard ('*') character")
                
            if len(errors) > 0:
                self.error("Footprint filter '{filter}' not correctly formatted".format(filter=filter))
                
                for error in errors:
                    self.errorExtra(error)
                
                self.bad_filters.append(filter)
        
    def check(self):
        """
        Proceeds the checking of the rule.
        """
        
        filters = self.component.fplist
        
        if len(filters) == 0:
            self.warning("No footprint filters defined")
            
        self.checkFilters(filters)
        
        return len(self.bad_filters) > 0

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("FIX: not supported")
