# -*- coding: utf-8 -*-

from __future__ import division

# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

from rules.rule import *
import re, os, math

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        self.expected_width=0.05
        self.expected_grid=0.01
        super(Rule, self).__init__(module, 'Rule 1.8', "Library files should use UNIX-style line-endings (LF)")
        
    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        
        return not module.unix_line_endings

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """

                    