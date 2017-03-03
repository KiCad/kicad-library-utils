# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, '3.3', 'Pins should not be placed on top of each other')

    def stackStr(self, stack):
        multi_unit = int(self.component.definition['unit_count']) > 1
        unit_str = " (unit {u})".format(stack['u']) if multi_unit else ""
        
        # WHY are pins flipped vertically? Mega sad face :(
        return "Pinstack @ ({x},{y}){u}".format(
            x = int(stack['x']),
            y = -1 * int(stack['y']),
            u = unit_str)
        
    def check(self):
        
        pin_locations = []
        
        for pin in self.component.pins:
            
            pinx = pin['posx']
            piny = pin['posy']
            pinu = pin['unit']
            
            dupe = False
            
            for loc in pin_locations:
            
                locx = loc['x']
                locy = loc['y']
                locu = loc['u']
                
                if pinx == locx and piny == locy and pinu == locu:
                    loc['pins'].append(pin)
                    dupe = True
                    
            if not dupe:
                new_loc = {'x': pinx, 'y': piny, 'u': pinu}
                new_loc['pins'] = [pin]
                pin_locations.append(new_loc)
                    
        err = False
                    
        for loc in pin_locations:
            if len(loc['pins']) > 1:
                
                pin_units = set()
                pin_nums = set()
                pin_names = set()
                pin_etypes = set()
                
                vis_pin_count = 0
                
                for pin in loc['pins']:
                    pin_nums.add(pin['num'])
                    pin_names.add(pin['name'])
                    pin_units.add(pin['unit'])
                    pin_etypes.add(pin['electrical_type'])
                    
                    # Add visibile pins
                    if not pin['pin_type'] == 'I':
                        vis_pin_count += 1
                    
                    # NC pins should never be stacked
                    if pin['electrical_type'] == 'N':
                        self.error("NC Pin {name} ({num}) @ ({x},{y}) is stacked on other pins".format(
                            name = pin['name'],
                            num = pin['num'],
                            x = pin['posx'],
                            y = pin['posy']))
                        err = True
                            
                # Fewer pin numbers than pins
                if len(pin_nums) < len(loc['pins']):
                    self.error("Duplicate pins @ ({x},{y}):".format(
                        x = loc['x'],
                        y = loc['y']))
                    err = True
                    for pin in loc['pins']: 
                        self.error("- Pin {name} ({num})".format(
                            name = pin['name'],
                            num = pin['num']))
                            
                    # If ALL pins are identical, go to next group (no further checks needed)
                    if len(pin_nums) == len(pin_names) == len(pin_units) == 1:
                        continue
                            
                # Different names!
                if len(pin_names) > 1:
                    self.error(self.stackStr(loc) + " have different names:")
                    err = True
                    for pin in loc['pins']:
                        self.error("- Pin {name} ({num})".format(
                            name = pin['name'],
                            num = pin['num']))
                            
                # Different types!
                if len(pin_etypes) > 1:
                    self.error(self.stackStr(loc) + " have different types:")
                    err = True
                    for pin in loc['pins']:
                        self.error("- Pin {name} ({num}) : {etype}".format(
                            name = pin['name'],
                            num = pin['num'],
                            etype = pinElectricalTypeToStr(pin['electrical_type'])))
            
                # Only one pin should be visible
                if not vis_pin_count == 1:
                    self.error(self.stackStr(loc) + " must have exactly one (1) invisible pin:")
                    err = True
                    for pin in loc['pins']:
                        self.error("- Pin {name} ({num}) is {vis}".format(
                            name = pin['name'],
                            num = pin['num'],
                            vis = 'INVISIBLE' if pin['pin_type'] == 'I' else 'VISIBLE'))

        return err
                    
    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.NORMAL, Severity.INFO, "FIX: not yet supported" )
        # TODO