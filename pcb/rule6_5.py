# -*- coding: utf-8 -*-

from rule import *

class Rule6_5(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule6_5, self).__init__('Rule 6.5', 'Silkscreen is not superposed to pads, its outline is completely visible after board assembly, uses 0.15mm line width and provides a reference mark for pin 1. (IPC-7351)')

    def check(self, module):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_silk_lines
            * b_silk_lines
            * bad_width_lines
        """
        self.f_silk_lines = module.filterLines('F.SilkS')
        self.b_silk_lines = module.filterLines('B.SilkS')

        # check the line width
        self.bad_width_lines = []
        for line in (self.f_silk_lines + self.b_silk_lines):
            if line['width'] != 0.15:
                self.bad_width_lines.append(line)

        return True if len(self.bad_width_lines) else False

    def fix(self, module):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if check_rule(module):
            for line in self.bad_width_lines:
                line['width'] = 0.15
