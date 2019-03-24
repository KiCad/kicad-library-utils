# -*- coding: utf-8 -*-

from rules.rule import *
import platform

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Library files must use Unix-style line endings (LF)')

    def check(self):

        # Only perform this check on linux systems (i.e. Travis)
        # Windows automatically checks out with CR+LF line endings
        if 'linux' in platform.platform().lower() and not checkLineEndings(self.module.filename):
            self.error("Incorrect line endings")
            self.errorExtra("Library files must use Unix-style line endings (LF)")
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """

        self.success("Line endings will be corrected on save")
