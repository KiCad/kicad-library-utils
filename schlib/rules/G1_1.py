# -*- coding: utf-8 -*-

from rules.rule import *
import string


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Illegal characters in symbol name')

    def check(self):

        allowed = string.digits + string.ascii_letters + "_-.+,"

        name = self.component.name.lower()

        illegal = ""

        for i, c in enumerate(name):
            if c in allowed:
                continue

            # Some symbols have a special character at the start
            if i == 0:
                if c in ['~', '#']:
                    continue

            # Illegal character found!
            illegal += c

        if len(illegal) > 0:
            self.error("Symbol name must contain only legal characters")
            self.errorExtra("Name '{n}' contains illegal characters '{i}'".format(n=self.component.name, i=illegal))
            return True
        else:
            # No errors!
            return False

    def fix(self):
        self.recheck()
