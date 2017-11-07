# -*- coding: utf-8 -*-

from rules.rule import *
import platform

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Illegal characters in footprint name')

    def check(self):

        allowed = string.digits + string.ascii_letters + "_-.+,"

        name = str(self.module.name).lower()

        illegal = ""

        for i, c in enumerate(name):
            if c in allowed:
                continue

            # Illegal character found!
            illegal += c

        if len(illegal) > 0:
            self.error("Footprint name must contain only legal characters")
            self.errorExtra("Name '{n}' contains illegal characters '{i}'".format(n=self.module.name, i=illegal))
            return True
        else:
            # No errors!
            return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        # Re-check line endings
        self.check()
