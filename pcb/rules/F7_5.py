# -*- coding: utf-8 -*-

from __future__ import division

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Annular ring must be at least 0.15mm')

    def checkPad(self, pad):
        if not 'size' in pad['drill']:
            self.error("Pad {n} drill data has no 'size' attribute".format(
                n = pad['number']))
            return True

        drill_size = pad['drill']['size']
        drill_x = drill_size['x']
        drill_y = drill_size['y']

        pad_size = pad['size']
        pad_x = pad_size['x']
        pad_y = pad_size['y']

        err = False

        MIN_RING = 0.15

        # Circular pad
        if drill_x == drill_y and pad_x == pad_y:
            # Round the number to 5 decimal places to prevent floating-point errors
            ring = round((pad_x - drill_x) / 2, 5)

            if ring < MIN_RING:
                self.error("Pad {n} annular ring ({d}mm) is below minimum ({mr}mm)".format(
                    n = pad['number'],
                    d = ring,
                    mr = MIN_RING))
                err = True

        # Non circular pad
        else:
            # Round the number to 5 decimal places to prevent floating-point errors
            ring_x = round((pad_x - drill_x) / 2, 5)

            if ring_x < MIN_RING:
                self.error("Pad {n} x-dimension annular ring ({d}mm) is below minimum ({mr}mm)".format(
                    n = pad['number'],
                    d = ring_x,
                    mr = MIN_RING))
                err = True

            # Round the number to 5 decimal places to prevent floating-point errors
            ring_y = round((pad_y - drill_y) / 2, 5)

            if ring_y < MIN_RING:
                self.error("Pad {n} y-dimension annular ring ({d}mm) is below minimum ({mr}mm)".format(
                    n = pad['number'],
                    d = ring_y,
                    mr = MIN_RING))
                err = True

        return err

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        module = self.module

        return any([self.checkPad(pad) for pad in module.filterPads('thru_hole')])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fix - not supported for this rule")
