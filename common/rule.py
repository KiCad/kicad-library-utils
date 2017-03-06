# -*- coding: utf-8 -*-

# Static functions
def isValidName(name):
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

class Verbosity:
    NONE=0
    NORMAL=1
    HIGH=2

class Severity:
    INFO=0
    WARNING=1
    ERROR=2
    SUCCESS=3

class KLCRuleBase(object):
    """
    A base class to represent a KLC rule
    """

    verbosity = 0
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.messageBuffer = []

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.messageBuffer=[]  

    #adds message into buffer only if such level of verbosity is wanted
    def verboseOut(self, msgVerbosity, severity, message):
        self.messageBuffer.append([message,msgVerbosity,severity])
        
    def warning(self, msg, verbosity=Verbosity.HIGH):
        self.verboseOut(verbosity, Severity.WARNING, msg)

    def error(self, msg, verbosity=Verbosity.HIGH):
        self.verboseOut(verbosity, Severity.ERROR, msg)
        
    def info(self, msg, verbosity=Verbosity.NORMAL):
        self.verboseOut(verbosity, Severity.INFO, msg)
        
    def success(self, msg, verbosity=Verbosity.HIGH):
        self.verboseOut(verbosity, Severity.SUCCESS, msg)
        
    def check(self, component):
        raise NotImplementedError('The check method must be implemented')

    def fix(self, component):
        raise NotImplementedError('The fix method must be implemented')

    def recheck(self):
        if self.check():
            self.error("Could not be fixed")
        else:
            self.success("Everything fixed")
            
    def hasOutput(self):
        return len(self.messageBuffer) > 0
            
    def processOutput(self, printer, verbosity=Verbosity.NONE, silent=False):
    
        if not verbosity:
            verbosity = 0

        # No violations
        if len(self.messageBuffer) == 0:
            return False
            
        else:
            printer.yellow("Violating " + self.name, indentation = 2)
            
        if verbosity > 0:
            printer.light_blue(self.description, indentation=4, max_width=100)
    
        for message in self.messageBuffer:
            v = message[1] # Verbosity of particular message
            msg = message[0]
            
            if v <= verbosity:
                if v == 0:
                    printer.gray(msg, indentation = 4)
                elif v == 1:
                    printer.brown(msg, indentation = 4)
                elif v == 2:
                    printer.red(msg, indentation = 4)
                elif v == 3:
                    printer.green(msg, indentation = 4)
                else:
                    printer.red("unknown severity: " + msg, indentation=4)
                    
        return True
