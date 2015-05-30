# -*- coding: utf-8 -*-

from rule import *

class Rule6_4(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule6_4, self).__init__('Rule 6.4', 'For surface-mount devices, footprint anchor is placed in the middle with respect to device lead ends. (IPC-7351).')

    def check(self, module):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pads_bounds
            * pads_distance
        """
        if module.attribute != 'smd':return ()

        self.pads_bounds = module.padsBounds()
        x = (self.pads_bounds['higher']['x'] - self.pads_bounds['lower']['x'])
        y = (self.pads_bounds['higher']['y'] - self.pads_bounds['lower']['y'])

        self.pads_distance = (x, y)

        if not (x == 0.0 and y == 0.0):
            return True

        return False

    def fix(self, module):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if check_rule(module):
            x = self.pads_bounds['lower']['x'] + (self.pads_distance['x'] / 2)
            y = self.pads_bounds['lower']['y'] + (self.pads_distance['y'] / 2)
            module.setAnchor((x, y))
