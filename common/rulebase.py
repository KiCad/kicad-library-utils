# -*- coding: utf-8 -*-

import inspect, os, sys
import json

def logError(log_file, rule_name, lib_name, item_name, warning=False):
    """
    Log KLC error output to a json file.
    The JSON file will contain a cumulative dict
    of the errors and the library items that do not comply.
    """

    if not log_file.endswith('.json'):
        log_file += '.json'

    if os.path.exists(log_file) and os.path.isfile(log_file):
        with open(log_file, 'r') as json_file:
            try:
                log_data = json.loads(json_file.read())
            except:
                print("Found bad JSON data - clearing")
                log_data = {}

    else:
        log_data = {}

    key = 'warnings' if warning else 'errors'

    if not key in log_data:
        log_data[key] = {}

    log_entry = {'library': lib_name, 'item': item_name}

    if not rule_name in log_data[key]:
        log_data[key][rule_name] = []

    log_data[key][rule_name].append(log_entry)

    # Write the log data back to file
    with open(log_file, 'w') as json_file:
        op = json.dumps(log_data, indent=4, sort_keys=True, separators=(',', ':'))
        json_file.write(op)

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

            if c in ['_', '-', '.', '+', ',']:
                continue

            return False

        return True

def checkLineEndings(filename):
    """
    Check for proper (Unix) line endings
    """
    filecontentsraw = open(filename, 'rb').readline()

    LE1 = ord(chr(filecontentsraw[-2]))
    LE2 = ord(chr(filecontentsraw[-1]))

    # 0x0D0A = Windows (CRLF)
    # 0x__0D = Mac OS 9 (CR)
    # 0x__0A = Unix (LF)
    if (LE1 == 0x0D and LE2 == 0x0A) or (LE2 == 0x0D):
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

    @property
    def name(self):
        path = inspect.getfile(self.__class__)
        path = os.path.basename(path)
        path = "".join(path.split(".")[:-1])
        return path.replace('_', '.')

    def __init__(self, description):
        self.description = description
        self.messageBuffer=[]
        self.resetErrorCount()
        self.resetWarningCount()


    def resetErrorCount(self):
        self.error_count = 0

    def resetWarningCount(self):
        self.warning_count = 0

    @property
    def errorCount(self):
        return self.error_count

    def hasErrors(self):
        return self.error_count > 0

    def warningCount(self):
        return self.warning_count

    @property
    def hasWarnings(self):
        return self.warning_count > 0

    #adds message into buffer only if such level of verbosity is wanted
    def verboseOut(self, msgVerbosity, severity, message):
        self.messageBuffer.append([message,msgVerbosity,severity])

    def warning(self, msg):
        self.warning_count += 1
        self.verboseOut(Verbosity.NORMAL, Severity.WARNING, msg)

    def warningExtra(self, msg):
        self.verboseOut(Verbosity.HIGH, Severity.WARNING, " - " + msg)

    def error(self, msg):
        self.error_count += 1
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

        self.resetErrorCount()
        self.resetWarningCount()

        self.check()

        if self.hasErrors():
            self.error("Could not fix all errors")
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
