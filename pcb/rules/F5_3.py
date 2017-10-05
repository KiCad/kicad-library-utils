# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Pad requirements for SMD footprints')

        self.required_layers = ["Cu", "Paste", "Mask"]
        self.sides = ["F.", "B."]

    def checkPads(self, pads):

        self.stencil_pads_with_number = []
        missing_layer_errors = []
        extra_layer_errors = []

        for pad in pads:
            layers = pad['layers']

            """
            A 'stencil' pad is used when a complex stencil shape is needed.
            - Only on F.Paste or B.Paste (or both)
            - Must not have a number (otherwise rats-nest is generated)
            """

            if all([lyr.endswith('.Paste') for lyr in layers]):
                if not pad['number'] == '':
                    self.stencil_pads_with_number.append(pad)
                continue

            # For SMD parts, following layers required:
            # F.Cu
            # F.Mask
            # F.Paste

            if not pad['type'] == 'smd':
                continue

            err = False

            # Check that required layers are present
            for layer in self.required_layers:
                present = False
                for side in self.sides:
                    lyr = side + layer
                    if lyr in layers:
                        present = True

                if not present:
                    missing_layer_errors.append("Pad '{n}' missing layer '{lyr}'".format(
                        n=pad['number'],
                        lyr=layer))

            # Check for extra layers
            allowed = []
            for layer in self.required_layers:
                for side in self.sides:
                    allowed.append(side + layer)

            for layer in layers:
                if layer not in allowed:
                    extra_layer_errors.append("Pad '{n}' has extra layer '{lyr}'".format(
                        n=pad['number'],
                        lyr=layer))
        err = False

        if len(self.stencil_pads_with_number) > 0:
            err = True
            self.error("Stencil pad(s) found with non-empty number")
            for p in self.stencil_pads_with_number:
                self.errorExtra("Pad '{n}' @ ({x}, {y})".format(n=p['number'], x=p['pos']['x'], y=p['pos']['y']))

        if len(extra_layer_errors) > 0:
            err = True
            self.error("Pad(s) found with extra layers")
            for e in extra_layer_errors:
                self.errorExtra(e)

        if len(missing_layer_errors) > 0:
            self.warning("Pad(s) potentially missing layers")
            for w in missing_layer_errors:
                self.warningExtra(w)

        return err

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        module = self.module

        return self.checkPads(module.filterPads("smd"))

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module

        for pad in self.stencil_pads_with_number:
            self.info("Removing number '{x}' for stencil pad".format(x=pad['number']))
            pad['number'] = ''

        self.recheck()