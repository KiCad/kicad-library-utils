# -*- coding: utf-8 -*-

from __future__ import division

# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        self.expected_width=0.05
        self.expected_grid=0.01
        super(Rule, self).__init__(module, 'Rule 6.6', "Courtyard line has a width {0}mm. This line is placed so that its clearance is measured from its center to the edges of pads and body, and its position is rounded on a grid of {1}mm.".format(self.expected_width,self.expected_grid))

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

        # check the width
        self.bad_width = []
        for graph in (self.f_courtyard_all + self.b_courtyard_all):
            if graph['width'] != self.expected_width:
                self.bad_width.append(graph)

        self.f_courtyard_lines = module.filterLines('F.CrtYd')
        self.b_courtyard_lines = module.filterLines('B.CrtYd')

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

                
        for  g in self.bad_width:
            self.verbose_message=self.verbose_message+"Some courtyard line has a width of {1}mm, different from {0}mm.\n".format(self.expected_width,g['width'])
        for  g in self.bad_grid:
            self.verbose_message=self.verbose_message+"Some courtyard line is not on the expected grid of {0}mm (line: {1}).\n".format(self.expected_grid,g['line'])
        if len(self.f_courtyard_all)+len(self.b_courtyard_all) == 0:
            self.verbose_message=self.verbose_message+"No courtyard line was found at all.\n"
        
        if (len(self.bad_width) > 0 or len(self.bad_grid) > 0 or len(self.f_courtyard_all)+len(self.b_courtyard_all) == 0):
            return True
        else:
            return False

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
                item['line']['start']['x'], item['line']['start']['y'] = x, y

                x, y = item['nanometers']['end']['x'], item['nanometers']['end']['y']
                x, y = round(x / self.expected_grid*1E6) * self.expected_grid, round(y / self.expected_grid*1E6) * self.expected_grid
                item['line']['end']['x'], item['line']['end']['y'] = x, y

            # TODO: create courtyard if does not exists
