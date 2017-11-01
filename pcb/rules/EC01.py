# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Stable pad shapes only')        

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        module = self.module

        # Allowed shapes
        allowed = ['circle', 'oval', 'rect', 'trapezoid']

        errors = []

        for pad in module.pads:
            if not pad['shape'].lower() in allowed:
                errors.append("Pad {n} has shape '{shape}'".format(
                                n = pad['number'],
                                shape = pad['shape']
                                ))

        if len(errors) > 0:
            self.error("Invalid pad shapes found")
            self.error("Allowed pad shapes are: " + ", ".join([shape for shape in allowed]))
            for err in errors:
                self.errorExtra(err)

        return len(errors) > 0

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fix - not supported for this rule")

