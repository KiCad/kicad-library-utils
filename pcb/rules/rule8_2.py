# -*- coding: utf-8 -*-

from __future__ import division

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args,'For surface-mount devices, footprint anchor is placed in the middle of the footprint (IPC-7351).')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pads_bounds
            * pads_distance
            * right_anchor
        """
        module = self.module
        if module.attribute != 'smd':
            # Ignore non-smd parts
            return False

        center = module.padMiddlePosition()

        err = False

        THRESHOLD = 0.001
        x = center['x']
        y = center['y']

        if abs(x) > THRESHOLD or abs(y) > THRESHOLD:
            self.error("Footprint anchor is not located at center of footprint")
            self.errorExtra("Footprint center calculated as ({x},{y})mm".format(
                x = round(center['x'], 5),
                y = round(center['y'], 5)))

            err = True

        return err

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            self.info("Footprint anchor fixed")

            center = module.padMiddlePosition()

            module.setAnchor([center['x'], center['y']])
