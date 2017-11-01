# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Pad requirements for THT footprints')

        self.required_layers = ["*.Cu","*.Mask"]

    def checkPads(self, pads):

        self.wrong_layers = []

        errors = []

        for pad in pads:
            layers = pad['layers']

            # For THT parts, following layers required:
            # *.Cu
            # F.Mask
            # B.Mask

            if not pad['type'] == 'thru_hole':
                continue

            err = False

            # check required layers
            for layer in self.required_layers:
                if layer not in layers:
                    errors.append("Pad '{n}' missing layer '{lyr}'".format(
                        n=pad['number'],
                        lyr=layer))
                    err = True

            # check for extra layers
            for layer in layers:
                if layer not in self.required_layers:
                    errors.append("Pad '{n}' has extra layer '{lyr}'".format(
                        n=pad['number'],
                        lyr=layer))
                    err = True

            if err:
                self.wrong_layers.append(pad)

        if len(errors) > 0:
            self.error("Some THT pads have incorrect layer settings")
            for msg in errors:
                self.errorExtra(msg)

        return len(self.wrong_layers) > 0

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        module = self.module

        return any([
            self.checkPads(module.filterPads('thru_hole'))
            ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module

        for pad in module.filterPads('thru_hole'):
            self.info("Pad {n} - Setting required layers for THT pad".format(n=pad['number']))
            pad['layers'] = self.required_layers

