# -*- coding: utf-8 -*-

class KLCRule(object):
    """
    A base class to represent a KLC rule
    """
    def __init__(self, component, name, description):
        self.component = component
        self.name = name
        self.description = description

    def check(self, component):
        raise NotImplementedError('The check method must be implemented')

    def fix(self, component):
        raise NotImplementedError('The fix method must be implemented')
