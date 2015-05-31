# -*- coding: utf-8 -*-

class KLCRule(object):
    """
    A base class to represent a KLC rule
    """
    def __init__(self, module, name, description):
        self.module = module
        self.name = name
        self.description = description

    def check(self, module):
        raise NotImplementedError('The check method must be implemented')

    def fix(self, module):
        raise NotImplementedError('The fix method must be implemented')
