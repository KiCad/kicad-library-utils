# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Pad 1 should be denoted by rectangular pad')

        self.names = ['1', 'A', 'A1', 'P1', 'PAD1']
        self.pad_1_shapes = ['rect', 'roundrect']

    def check(self):

        # Skip checks for non THT parts
        if not self.module.attribute == 'pth':
            return False

        pad_1_rectangular = True
        other_pads_rectangular = False

        for pad in self.module.pads:
            num = pad['number']

            # Pin 1!
            if str(num).upper() in self.names:
                if not pad['shape'] in self.pad_1_shapes:
                    pad_1_rectangular = False

            else:
                if pad['shape'] in self.pad_1_shapes:
                    other_pads_rectangular = True

        if not pad_1_rectangular and len(self.module.pads) >= 2:
            self.warning("Pad 1 should be rectangular")
            self.warningExtra("Ignore for non-polarized devices")

        if other_pads_rectangular:
            self.warning("Only pad 1 should be rectangular")

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module

        for pad in module.filterPads('thru_hole'):
            self.info("Pad {n} - Setting required layers for THT pad".format(n=pad['number']))
            pad['layers'] = self.required_layers
