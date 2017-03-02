# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, '3.3', 'Pins should not be placed on top of each other')
        
    def check(self):
        
        pin_locations = []
        
        for pin in self.component.pins:
            
            pinx = pin['posx']
            piny = pin['posy']
            
            dupe = False
            
            for loc in pin_locations:
            
                locx = loc['x']
                locy = loc['y']
                
                if pinx == locx and piny == locy:
                    loc['pins'].append(pin)
                    dupe = True
                    
            if not dupe:
                new_loc = {'x': pinx, 'y': piny}
                new_loc['pins'] = [pin]
                pin_locations.append(new_loc)
                    
        err = False
                    
        for loc in pin_locations:
            if len(loc['pins']) > 1:
                self.error("Multiple pins at ({x},{y}):".format(x=loc['x'], y=loc['y']))
                err = True
                for pin in loc['pins']:
                    self.error("- Pin {name} ({num})".format(name=pin['name'], num=pin['num']))

        return err
                    
    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.NORMAL, Severity.INFO, "FIX: not yet supported" )
        # TODO