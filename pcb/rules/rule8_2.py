# -*- coding: utf-8 -*-

from __future__ import division

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Rule 8.2', 'For surface-mount devices, footprint anchor is placed in the middle of the footprint (IPC-7351).')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pads_bounds
            * pads_distance
            * right_anchor
        """
        module = self.module
        if module.attribute != 'smd':return ()

        self.pads_bounds = module.padsBounds()
        x = (self.pads_bounds['higher']['x'] - self.pads_bounds['lower']['x'])
        y = (self.pads_bounds['higher']['y'] - self.pads_bounds['lower']['y'])
        self.pads_distance = {'x':x, 'y':y}

        x = self.pads_bounds['lower']['x'] + (self.pads_distance['x'] / 2)
        y = self.pads_bounds['lower']['y'] + (self.pads_distance['y'] / 2)
        self.right_anchor = {'x':x, 'y':y}

        if not (x == 0.0 and y == 0.0):
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.setAnchor((self.right_anchor['x'], self.right_anchor['y']))
