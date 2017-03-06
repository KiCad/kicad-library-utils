# -*- coding: utf-8 -*-

import string

class KLCRule(object):
    """
    A base class to represent a KLC rule
    """
    def __init__(self, module, args, name, description,verbose_message='',fix_message=''):
        self.module = module
        self.name = name
        self.description = description
        self.args = args
        
        self.verbose_message=[]
        self.addMessage(verbose_message)

        self.fix_message = []
        self.addFixMessage(fix_message)
        
        # Illegal chars
        self.illegal_chars = ['*', '?', ':', '/', '\\', '[', ']', ';', '|', '=', ',']
        
    def isValidName(self, name):
        name = str(name).lower()
        for c in name:
            # Numeric characters
            if c.isnumeric():
                continue
                
            # Alpha characters (simple set only)
            if c >= 'a' and c <= 'z':
                continue
                
            if c in ['_', '-', '.']:
                continue
            
            return False
                
        return True

    def check(self, module):
        raise NotImplementedError('The check method must be implemented')

    def fix(self, module):
        raise NotImplementedError('The fix method must be implemented')
        
    def filterMsg(self, msg):
        msg = msg.strip()
        
        return msg
        
    def addMessage(self, msg):
        if msg:
            self.verbose_message.append(self.filterMsg(msg))

    def addFixMessage(self, msg):
        if msg:
            self.fix_message.append(self.filterMsg(msg))
