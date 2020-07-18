# -*- coding: utf-8 -*-

from __future__ import division

from rules.rule import *
from math import sqrt

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
            * center_pads
            * center_fab

        This test will generate false positives for parts that have a weird outline, are not symmetrical or do not have 
        the pick'n'place location in the geometrical center.
        Most connectors will have at least one of those issues (e.g. a FPC-Connector) and fail this test.
        For most other components (LEDs, molded packages, ...) this test will yield usable results.
        """
        module = self.module
        if module.attribute != 'smd':
            # Ignore non-smd parts
            return False

        center_pads = module.padMiddlePosition()
        center_fab  = module.geometricBoundingBox("F.Fab").center

        err = False

        # calculate the distance from origin for the pads and fab
        diff_pads = sqrt(center_pads['x']**2 + center_pads['y']**2)
        diff_fab  = sqrt(center_fab['x']**2 +  center_fab['y']**2)
        # select the xy coordinates that are closest to the center
        if diff_pads > diff_fab:
            (x, y) = (center_fab['x'], center_fab['y'])
        else:
            (x, y) = (center_pads['x'], center_pads['y'])

        THRESHOLD = 0.001
        if abs(x) > THRESHOLD or abs(y) > THRESHOLD:
            self.error("Footprint anchor does not match calculated center of Pads or F.Fab")
            self.errorExtra("calculated center for Pads [{xp},{yp}mm]".format(
                xp = round(center_pads['x'], 5),
                yp = round(center_pads['y'], 5)))
            self.errorExtra("calculated center for F.Fab [{xf},{yf}mm]".format(
                xf = round(center_fab['x'], 5),
                yf = round(center_fab['y'], 5)))

            err = True

        return err

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        This fix will always use the pads center position.
        """
        module = self.module
        if self.check():
            self.info("Footprint anchor fixed")

            center = module.padMiddlePosition()

            module.setAnchor([center['x'], center['y']])
