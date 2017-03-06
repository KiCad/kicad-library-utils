# -*- coding: utf-8 -*-

import string
import sys
sys.path.append("..\..\common")

from rule import *

class KLCRule(KLCRuleBase):
    """
    A base class to represent a KLC rule
    """
    def __init__(self, module, args, name, description):
    
        KLCRuleBase.__init__(self, name, description)
    
        self.module = module
        self.args = args
        
        # Illegal chars
        self.illegal_chars = ['*', '?', ':', '/', '\\', '[', ']', ';', '|', '=', ',']
