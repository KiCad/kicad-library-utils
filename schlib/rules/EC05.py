# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC05 - Extra Checking', 'Pin numbers should not be duplicated.')

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
                if p['num'] == pin['num']:
                    self.verboseOut(Verbosity.NORMAL, Severity.WARNING, "Pin {n} is duplicated".format(n=pin['num']))
                    self.verboseOut(Verbosity.HIGH, Severity.ERROR, 'pin: {0} ({1})'.format(pin['name'], pin['num']))
                    self.verboseOut(Verbosity.HIGH, Severity.ERROR, 'pin: {0} ({1})'.format(p['name'], p['num']))
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
