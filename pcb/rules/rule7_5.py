# -*- coding: utf-8 -*-

from __future__ import division

# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

from rules.klc_constants import *
from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        self.expected_width=KLC_CRTYD_WIDTH
        self.expected_grid=KLC_CRTYD_GRID
        super(Rule, self).__init__(module, 'Rule 7.5', "Courtyard requirements".format(self.expected_width,self.expected_grid))

    # Check that the courtyard is present
    # Return True if present
    def checkMissingCourtyard(self):
        if len(self.f_courtyard_all)+len(self.b_courtyard_all) == 0:
            self.addMessage("No courtyard line was found.\n")
            return True
            
        return False
    
    # Check that the courtyard width is correct
    def checkIncorrectWidth(self):
        # check the width
        self.bad_width = []
        for graph in (self.f_courtyard_all + self.b_courtyard_all):
            if graph['width'] != self.expected_width:
                self.bad_width.append(graph)
                
        for  g in self.bad_width:
            self.addMessage("Some courtyard line has a width of {1}mm, different from {0}mm.\n".format(self.expected_width,g['width']))
        
        # return True if bad width detected
        return len(self.bad_width) > 0
    
    def checkCourtyardGrid(self):
        # check if there is proper rounding 0.01 of courtyard lines
        # convert position to nanometers (add/subtract 1/10^7 to avoid wrong rounding and cast to int)
        # int pos_x = (d_pos_x + ((d_pos_x >= 0) ? 0.0000001 : -0.0000001)) * 1000000;
        # int pos_y = (d_pos_y + ((d_pos_y >= 0) ? 0.0000001 : -0.0000001)) * 1000000;
        self.bad_grid = []
        for line in (self.f_courtyard_lines + self.b_courtyard_lines):
            nanometers = {}
            x, y = line['start']['x'], line['start']['y']
            x = int( (x + (0.0000001 if x >= 0 else -0.0000001))*1E6 )
            y = int( (y + (0.0000001 if y >= 0 else -0.0000001))*1E6 )
            start_is_wrong = (x % int(self.expected_grid*1E6)) or (y % int(self.expected_grid*1E6))
            nanometers['start'] = {'x':x, 'y':y}

            x, y = line['end']['x'], line['end']['y']
            x = int( (x + (0.0000001 if x >= 0 else -0.0000001))*1E6 )
            y = int( (y + (0.0000001 if y >= 0 else -0.0000001))*1E6 )
            end_is_wrong = (x % int(self.expected_grid*1E6)) or (y % int(self.expected_grid*1E6))
            nanometers['end'] = {'x':x, 'y':y}

            if start_is_wrong or end_is_wrong:
                self.bad_grid.append({'nanometers':nanometers, 'line':line})
                
        for g in self.bad_grid:
            self.addMessage("Some courtyard line is not on the expected grid of {0}mm (line: {1}).\n".format(self.expected_grid,g['line']))
        
        # return True if error detected
        return len(self.bad_grid) > 0
    
    def checkCourtyardClearance(self):
        
        ## TODO
        return False
        
    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_courtyard_all
            * b_courtyard_all
            * f_courtyard_lines
            * b_courtyard_lines
            * bad_width
            * bad_grid
        """
        module = self.module
        self.f_courtyard_all = module.filterGraphs('F.CrtYd')
        self.b_courtyard_all = module.filterGraphs('B.CrtYd')

        self.f_courtyard_lines = module.filterLines('F.CrtYd')
        self.b_courtyard_lines = module.filterLines('B.CrtYd')     
            
        # Return True if any of the checks returned True (indicating failure)
        return any([ 
                self.checkMissingCourtyard(),
                self.checkIncorrectWidth(),
                self.checkCourtyardGrid(),
                self.checkCourtyardClearance()
                ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            for graph in self.bad_width:
                graph['width'] = self.expected_width

            for item in self.bad_grid:
                x, y = item['nanometers']['start']['x'], item['nanometers']['start']['y']
                x, y = round(x / self.expected_grid*1E6) * self.expected_grid, round(y / self.expected_grid*1E6) * self.expected_grid
                item['nanometers']['start']['x'], item['nanometers']['start']['y'] = x, y

                x, y = item['nanometers']['end']['x'], item['nanometers']['end']['y']
                x, y = round(x / self.expected_grid*1E6) * self.expected_grid, round(y / self.expected_grid*1E6) * self.expected_grid
                item['nanometers']['end']['x'], item['nanometers']['end']['y'] = x, y

            # TODO: create courtyard if does not exists
