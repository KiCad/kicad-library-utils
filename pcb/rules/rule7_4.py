# -*- coding: utf-8 -*-

from __future__ import division


# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

from klc_constants import *
from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 7.4', "Fabrication layer requirements")

    # Check for presence of component value
    def checkMissingValue(self):
        mod = self.module
        error = False
        
        if mod.value['layer'] not in ['F.Fab', 'B.Fab']:
            self.addMessage("Component value is on layer {lyr} but should be on F.Fab or B.Fab".format(lyr=mod.value['layer']))
            error = True
        if mod.value['font']['height'] > KLC_TEXT_HEIGHT:
            self.addMessage("Value label has a height of {1}mm (expected: <={0}mm".format(KLC_TEXT_HEIGHT, mod.value['font']['height']))
            error = True
        if mod.value['font']['height'] > KLC_TEXT_WIDTH:
            self.addMessage("Value label has a width of {1}mm (expected: <={0}mm".format(KLC_TEXT_WIDTH, mod.value['font']['width']))
            error = True
        if mod.value['font']['thickness'] != KLC_TEXT_THICKNESS:
            self.addMessage("Value label has a thickness of {1}mm (expected: {0}mm".format(KLC_TEXT_THICKNESS, mod.values['font']['thickness']))
            error = True

        return error
    
    def checkMissingLines(self):
        if len(self.f_fabrication_all) + len(self.b_fabrication_all) == 0:
            self.addMessage("No drawings found on fabrication layer.\n")
            return True
            
        return False
    
    # Check fab line widths
    def checkIncorrectWidth(self):
        self.bad_fabrication_width = []
        for graph in (self.f_fabrication_all + self.b_fabrication_all):
            if graph['width'] != KLC_FAB_WIDTH:
                self.bad_fabrication_width.append(graph)
    
        for g in self.bad_fabrication_width:
            self.addMessage("Some fabrication layer line has a width of {1}mm, different from {0}mm.\n".format(KLC_FAB_WIDTH,g['width']))
        
        return len(self.bad_fabrication_width) > 0
        
    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_fabrication_all
            * b_fabrication_all
            * f_fabrication_lines
            * b_fabrication_lines
            * bad_fabrication_width
        """
        module = self.module
        self.f_fabrication_all = module.filterGraphs('F.Fab')
        self.b_fabrication_all = module.filterGraphs('B.Fab')

        self.f_fabrication_lines = module.filterLines('F.Fab')
        self.b_fabrication_lines = module.filterLines('B.Fab')
                
        return any([
                    self.checkMissingValue(),
                    self.checkMissingLines(),
                    self.checkIncorrectWidth()
                    ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.checkIncorrectWidth():
            for graph in self.bad_fabrication_width:
                graph['width'] = KLC_FAB_WIDTH
                
        if self.checkMissingValue():
            module.value['layer'] = 'F.Fab'
            module.value['font']['height'] = self.expected_val_width
            module.value['font']['width'] = self.expected_val_width
            module.value['font']['thickness'] = self.expected_val_thickness

