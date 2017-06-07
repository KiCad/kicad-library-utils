# -*- coding: utf-8 -*-

# Static functions
def isValidName(name, checkForGraphicSymbol=False, checkForPowerSymbol=False):
        name = str(name).lower()
        firstChar=True
        for c in name:
            # first character may be '~' in some cases
            if (checkForPowerSymbol or checkForGraphicSymbol) and firstChar and c=='~':
                continue
            
            firstChar=False
            # Numeric characters check
            if c.isalnum():
                continue
                
            # Alpha characters (simple set only)
            if c >= 'a' and c <= 'z':
                continue
                
            if c in ['_', '-', '.']:
                continue
            
            if checkForPowerSymbol and (c in ['+']):
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
        
    def warning(self, msg):
        self.verboseOut(Verbosity.NORMAL, Severity.WARNING, msg)

    def warningExtra(self, msg):
        self.verboseOut(Verbosity.HIGH, Severity.WARNING, " - " + msg)
        
    def error(self, msg):
        self.verboseOut(Verbosity.NORMAL, Severity.ERROR, msg)
        
    def errorExtra(self, msg):
        self.verboseOut(Verbosity.HIGH, Severity.ERROR, " - " + msg)
        
    def info(self, msg):
        self.verboseOut(Verbosity.NONE, Severity.INFO, "> " + msg)
        
    def success(self, msg):
        self.verboseOut(Verbosity.NORMAL, Severity.SUCCESS, msg)
        
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
        else:
            verbosity = int(verbosity)

        # No violations
        if len(self.messageBuffer) == 0:
            return False

        if verbosity > 0:
            printer.light_blue(self.description, indentation=4, max_width=100)
    
        for message in self.messageBuffer:
            v = message[1] # Verbosity
            s = message[2] # Severity
            msg = message[0]
            
            if v <= verbosity:
                if s == 0:
                    printer.gray(msg, indentation = 4)
                elif s == 1:
                    printer.brown(msg, indentation = 4)
                elif s == 2:
                    printer.red(msg, indentation = 4)
                elif s == 3:
                    printer.green(msg, indentation = 4)
                else:
                    printer.red("unknown severity: " + msg, indentation=4)
                    
        # Clear message buffer
        self.messageBuffer = []
        return True
