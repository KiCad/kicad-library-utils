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

            # get pads positions
            for pad in pads:
                self.pin1_position.append((pad['pos']['x'], pad['pos']['y']))

            # check how many pin 1 was found
            if self.pin1_count != 1:
                return True

            # if reach here there is only one pin 1
            self.pin1_position = self.pin1_position[0]
            pad1 = pads[0]

            # check pin 1 position
            if pad1['pos']['x'] != 0 or pad1['pos']['y'] != 0:
                return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            if self.pin1_count == 1:
                module.setAnchor(self.pin1_position)
