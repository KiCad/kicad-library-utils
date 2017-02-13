# -*- coding: utf-8 -*-

class KLCRule(object):
    """
    A base class to represent a KLC rule
    """
    def __init__(self, module, name, description,verbose_message=''):
        self.module = module
        self.name = name
        self.description = description
        
        self.verbose_message=[]
        
        self.addMessage(verbose_message)

    def check(self, module):
        raise NotImplementedError('The check method must be implemented')

    def fix(self, module):
        raise NotImplementedError('The fix method must be implemented')

    def addMessage(self, msg):
        if msg:
            self.verbose_message.append(msg.strip())