# -*- coding: utf-8 -*-

#this should go to separate file
def pinElectricalTypeToStr(pinEType):
    pinMap={"I":"INPUT",\
    "O":"OUTPUT",\
    "B":"BIDI",\
    "T":"TRISTATE",\
    "P":"PASSIVE",\
    "U":"UNSPECIFIED",\
    "W":"POWER INPUT",\
    "w":"POWER OUTPUT",\
    "C":"OPEN COLLECTOR",\
    "E":"OPEN EMITTER",\
    "N":"NOT CONNECTED"}
    if pinEType in pinMap.keys():
        return pinMap[pinEType]
    else:
        return "INVALID"

def pinTypeToStr(pinType):
    pinMap={"I":"INVERTED",\
    "C":"CLOCK",\
    "CI":"INVERTED CLOCK",\
    "L":"INPUT LOW",\
    "CL":"CLOCK LOW",\
    "V":"OUTPUT LOW",\
    "F":"FALLING EDGE CLOCK",\
    "X":"NON LOGIc"}
    if pinType in pinMap.keys():
        return pinMap[pinType]
    else:
        return "INVALID"

def backgroundFillToStr(bgFill):
    bgMap={
    "F":"FOREGROUND",
    "f":"BACKGROUND",
    "N":"TRANSPARENT"}
    if bgFill in bgMap.keys():
        return bgMap[bgFill]
    else:
        return "INVALID"

def positionFormater(element):
    if type(element) != type({}):
        raise Exception("input type: ",type(element),"expected dictionary, ",element)
    if(not {"posx","posy"}.issubset(element.keys())):
        raise Exception("missing keys 'posx' and 'posy' in"+str(element))
    return "posx {0}, posy {1}".format(element['posx'],element['posy'])
    # return "pos [{0},{1}]".format(element['posx'],element['posy'])

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

    verbosity = 0

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

    def recheck(self):
        if self.check():
            self.verboseOut(Verbosity.HIGH, Severity.ERROR,"...could't be fixed")
        else:
            self.verboseOut(Verbosity.HIGH, Severity.SUCCESS,"everything fixed")
