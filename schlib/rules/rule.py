# -*- coding: utf-8 -*-

class Verbosity:
    NONE=0
    NORMAL=1
    HIGH=2

class Severity:
    INFO=0
    WARNING=1
    ERROR=2
    SUCCESS=3

class KLCRule(object):
    """
    A base class to represent a KLC rule
    """

    def __init__(self, component, name, description):
        self.component = component
        self.name = name
        self.description = description
        self.messageBuffer=[]

    #adds message into buffer only if such level of verbosity is wanted
    def verboseOut(self, msgVerbosity, severity, message):
        self.messageBuffer.append([message,msgVerbosity,severity])

    def check(self, component):
        raise NotImplementedError('The check method must be implemented')

    def fix(self, component):
        raise NotImplementedError('The fix method must be implemented')
