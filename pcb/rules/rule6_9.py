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
        self.expected_width=0.1
        super(Rule, self).__init__(module, 'Rule 6.9', "Fabrication layer contains an outline of the part using a {0}mm line width.".format(self.expected_width))

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

        # check the width
        self.bad_fabrication_width = []
        for graph in (self.f_fabrication_all + self.b_fabrication_all):
            if graph['width'] != self.expected_width:
                self.bad_fabrication_width.append(graph)

        self.f_fabrication_lines = module.filterLines('F.Fab')
        self.b_fabrication_lines = module.filterLines('B.Fab')


                
        for  g in self.bad_fabrication_width:
            self.verbose_message=self.verbose_message+"Some fabrication layer line has a width of {1}mm, different from {0}mm.\n".format(self.expected_width,g['width'])
        if len(self.f_fabrication_all) + len(self.b_fabrication_all) == 0:
            self.verbose_message=self.verbose_message+"No drawings found on fabrication layer at all.\n"
        
        if (len(self.bad_fabrication_width) > 0 or len(self.f_fabrication_all) +len(self.b_fabrication_all) == 0):
            return True
        else:
            return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            for graph in self.bad_fabrication_width:
                graph['width'] = self.expected_width

