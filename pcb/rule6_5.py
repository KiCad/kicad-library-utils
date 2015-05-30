# -*- coding: utf-8 -*-

from rule import *

class Rule6_5(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule6_5, self).__init__('Rule 6.5', 'Silkscreen is not superposed to pads, its outline is completely visible after board assembly, uses 0.15mm line width and provides a reference mark for pin 1. (IPC-7351).')

    def check(self, module):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_silk
            * b_silk
            * bad_width
        """
        self.f_silk = module.filterGraphs('F.SilkS')
        self.b_silk = module.filterGraphs('B.SilkS')

        # check the width
        self.bad_width = []
        for graph in (self.f_silk + self.b_silk):
            if graph['width'] != 0.15:
                self.bad_width.append(graph)

        return True if len(self.bad_width) else False

    def fix(self, module):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check(module):
            for graph in self.bad_width:
                graph['width'] = 0.15
