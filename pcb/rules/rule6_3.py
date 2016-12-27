# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 6.3', 'For through-hole components, footprint anchor is set on pad 1.')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        module = self.module
        # check if module is through-hole
        if module.attribute == 'pth':
            pads = module.getPadsByNumber(1)
            self.pin1_count = len(pads)
            self.pin1_position = []

            # check/get pads positions
            anchor_ok = False
            for pad in pads:
                x, y = pad['pos']['x'], pad['pos']['y']
                self.pin1_position.append((x, y))
                if x == 0 and y == 0:
                    anchor_ok = True
                else:
                    self.verbose_message=self.verbose_message+"pin1 was found at x={0}mm y={1}mm. ".format(x,y)

            return not anchor_ok

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.setAnchor(min(self.pin1_position))
