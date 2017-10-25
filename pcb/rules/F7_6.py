# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Minimum hole drill size')

    def checkPad(self, pad):

        if 'drill' not in pad:
            self.error("Pad {p} is missing 'drill' parameter".format(p=pad['number']))
            return True

        drill = pad['drill']

        if 'size' not in drill:
            self.error("Drill specification is missing 'size' parameter for pad {p}".format(p=pad['number']))
            return True

        size = min(drill['size']['x'], drill['size']['y'])

        err = False

        if size < 0.20:
            self.error("Pad {n} min. drill size ({d}mm) is below minimum (0.20mm)".format(
                n = pad['number'],
                d = size))
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
