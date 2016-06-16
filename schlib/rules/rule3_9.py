# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.9', 'Pin numbers should not be duplicated for a symbol.')

    def check(self):
        """
        Proceeds the checking of the rule.
        Determines if any symbol pins are duplicated
        """
        
        pins = []
        duplicates = []
        
        #look for duplicate pins
        for pin in self.component.pins:
            found = False
            for p in pins:
                if p['num'] == pin['num'] and not p['name'] == pin['name']:
                    self.verboseOut(Verbosity.NORMAL, Severity.WARNING, "Pin {n} is duplicated".format(n=pin['num']))
                    self.verboseOut(Verbosity.HIGH, Severity.INFO, "Pin '{n1}' is a duplicate of pin '{n2}'".format(
                        n1 = pin['name'],
                        n2 = p['name']))
                    found = True
                    break
                    
            if not found:
                pins.append(pin)

            else:
                duplicates.append(pin)
           
        return len(duplicates) > 0

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.NORMAL, Severity.INFO, "FIX: not supported" )
