# -*- coding: utf-8 -*-

from rule import *

class Rule6_3(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule6_3, self).__init__('Rule 6.3', 'For through-hole components, footprint anchor is set on pad 1.')

    def check(self, module):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        # check if module is through-hole
        if module.attribute == 'pth':
            pads = module.getPadsByNumber(1)
            self.pin1_count = len(pads)
            self.pin1_position = []

            # get pads positions
            for pad in pads:
                self.pin1_position.append((pad['pos']['x'], pad['pos']['y']))

            # check if there is more than one pin numbered as 1
            if self.pin1_count > 1:
                return True

            # if reach here there is only one pin 1
            self.pin1_position = self.pin1_position[0]
            pad1 = pads[0]

            # check pin 1 position
            if pad1['pos']['x'] != 0 or pad1['pos']['y'] != 0:
                return True

        return False

    def fix(self, module):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if check_rule(module):
            module.setAnchor(self.pin1_position)
