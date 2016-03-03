#!/usr/bin/env python3

import sys,os,math
from lxml import etree
import re

SPECIAL_PIN_MAPPING = {"VSS/TH": ["VSS/TH"],
                       "PC13-ANTI_TAMP": ["PC13", "ANTI_TAMP"],
                       "PB2/BOOT1": ["PB2", "BOOT1"],
                       "PC14OSC32_IN": ["PC14"],
                       "PC15OSC32_OUT": ["PC15"], 
                       "PF11BOOT0": ["PF11"],
                       "OSC_IN": [""],
                       "OSC_OUT": [""]}

SPECIAL_TYPES_MAPPING = {"RCC_OSC_IN": "Clock", "RCC_OSC_OUT": "Clock"}

PIN_TYPES_MAPPING = {"Power": "W", "I/O": "B", "Reset": "I", "Boot": "I", 
                     "MonoIO": "B", "NC": "N", "Clock": "I"}

BOOT1_FIX_PARTS = {r"^STM32F10\d.+$", r"^STM32F2\d\d.+$", r"^STM32F4\d\d.+$", 
                   r"^STM32L1\d\d.+$"}

def unique(items):
    found = set([])
    keep = []

    for item in items:
        if item not in found:
            found.add(item)
            keep.append(item)

    return keep

class pin:
    def __init__(self, pinnumber, name, pintype):
        if not (name in SPECIAL_PIN_MAPPING):
            splname = name.split("/");
            realname = splname[0]
            splname2 = splname[0].split("-")
            if (len(splname2) > 1 and splname2[1] != ""):
                realname = splname2[0]
            altf = []
        else:
            realname = SPECIAL_PIN_MAPPING[name][0]
            altf = SPECIAL_PIN_MAPPING[name][1:]

        self.pinnumber = pinnumber
        self.name = realname
        self.fullname = name
        self.pintype = pintype
        self.altfunctions = altf
        self.drawn = False  # Whether this pin has already been included in the component or not
        self.x = 0;
        self.y = 0;
        self.placed = False

    def createPintext(self, left):
        if (left):
            if (self.name == ""):
                s = "/".join(self.altfunctions)
            else:
                s = "/".join(self.altfunctions + [self.name])
        else:
            if (self.name == ""):
                s = "/".join(self.altfunctions)
            else:
                s = "/".join([self.name] + self.altfunctions)
        self.pintext = s.replace(" ","")

class device:
    def __init__(self, xmlfile, pdfdir):
        print(xmlfile)
        self.xmlfile = xmlfile
        self.pdfdir = pdfdir
        self.name = ""
        self.package = ""
        self.pins = []
        self.aliases = []

        self.readxml()
        self.readpdf()
        self.createComponent()
        self.createDocu()

    def readxml(self):
        self.tree = etree.parse(self.xmlfile)
        self.root = self.tree.getroot()

        self.ns = {"a": self.root.nsmap[None]}  # I hate XML

        name = self.root.get("RefName")

        als = re.search(r"^(.+)\((.+)\)(.+)$", name)
        if (als):
            pre = als.group(1)
            post = als.group(3)
            s = als.group(2).split("-")
            self.name = pre + s[0] + post
            for a in s[1:]:
                self.aliases.append(pre + a + post)
        else:
            self.name = name

        self.package = self.root.get("Package")
        
        self.bga = False
        for child in self.root.xpath("a:Pin", namespaces=self.ns):
            # Create object and read attributes
            newpin = pin(child.get("Position"), child.get("Name"), child.get("Type"))
            try:
                int(child.get("Position"))
            except ValueError:
                self.bga = True

            for signal in child.xpath("a:Signal",namespaces=self.ns):
                altfunction = signal.get("Name")
                if(not altfunction == "GPIO"):   # No need to add GPIO as alt function
                    newpin.altfunctions.append(altfunction)
                if(altfunction in SPECIAL_TYPES_MAPPING):
                    newpin.pintype = SPECIAL_TYPES_MAPPING[altfunction]
                    
            if newpin.name == "PB2":
                for pre in BOOT1_FIX_PARTS:
                    if re.search(pre, name) and (not ("BOOT1" in newpin.altfunctions)):
                        print("Fixing PB2/BOOT1 for part " + name)
                        print("  " + newpin.name + " " + str(newpin.altfunctions))
                        newpin.altfunctions.insert(0, "BOOT1")
                    
                    
            self.pins.append(newpin)
        if(self.root.get("HasPowerPad") == "true"):    # Special case for the thermal pad
            # Some heuristic here
            packPinCountR = re.search(r"^[a-zA-Z]+([0-9]+)$", self.package)
            powerpinnumber = int(packPinCountR.group(1)) + 1
            print("Device " + name + " with powerpad, package " + self.package + ", power pin: " + str(powerpinnumber))
            powerpadpin = pin(powerpinnumber, "VSS", "Power")
            self.pins.append(powerpadpin)

        
        if(not self.bga):
            for apin in self.pins:
                apin.pinnumber = int(apin.pinnumber)

        # Parse information for documentation
        self.core = self.root.xpath("a:Core", namespaces=self.ns)[0].text
        self.family = self.root.get("Family")
        self.line = self.root.get("Line")
        try:
            self.freq = self.root.xpath("a:Frequency", namespaces=self.ns)[0].text
        except:
            self.freq = None    # Some devices don't have a frequency specification... thanks obama!
        self.ram = self.root.xpath("a:Ram", namespaces=self.ns)[0].text
        self.io = self.root.xpath("a:IONb", namespaces=self.ns)[0].text
        self.flash = self.root.xpath("a:Flash", namespaces=self.ns)[0].text
        try:
            self.voltage = [self.root.xpath("a:Voltage", namespaces=self.ns)[0].get("Min", default="--"), self.root.xpath("a:Voltage", namespaces=self.ns)[0].get("Max", default="--")]
        except:
            self.voltage = None # Some devices don't have a voltage specification also

    def xcompare(self, x, y):
        l = min(len(x), len(y))
        for i in range(0, l):
            if ((x[i] != 'x') and (y[i] != 'x') and (x[i] != y[i])):
                return False
        return True

    def readpdf(self):
        self.pdf = "NOSHEET"
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.pdfdir):
            files.extend(filenames)
            break

        s = self.name

        #print("NEW: " + s)
        candidatestring = {}
        for pdf in files:
            if(pdf.endswith(".pdf.par")):   # Find all processed PDF files and open them for evaluation
                p = open(os.path.join(self.pdfdir, pdf), "r")
                for line in p:
                    if(line.find(s[:8]) >= 0):
                        candidatenames = line.rstrip().translate(str.maketrans(","," ")).split()    # Remove newline and commas and then split string
                        for candidatename in candidatenames:
                            candidatestring[candidatename] = pdf    # Associate file with every device name
                    if(not line.startswith("STM32")):   # Assume that the device names are always at the beginning of file
                        break
        #print(candidatestring)  # TODO: CONTINUE HERE!!!!
        keystokeep = []
        for key in candidatestring:
            # Some heuristic here
            minussplit = key.split("-")
            variants = minussplit[0].split("/")
            if (len(minussplit) > 1):
                suffix = "x" + "x".join(minussplit[1:])
            else:
                suffix = ""
            strings = [suffix + variants[0]]
            for var in variants[1:]:
                strings.append(strings[0][:-len(var)] + var + suffix)
            for string in strings:
                if self.xcompare(s, string):
                    keystokeep.append(key)
        
        winners = []    # I got too tired of this
        for key in unique(keystokeep):
            try:
                winners.append(candidatestring.pop(key))
            except:
                pass

        #print(winners)
        if(len(winners) > 0):
            firstwinner = winners[0]
            #print(winners)
            for winner in winners:
                if(winner == firstwinner):
                    self.pdf = winner[:-4]
                else:
                    print("Multiple datasheet determined for this device: " + self.name + "(" + str(winners) + ")")
                    self.pdf = "NOSHEET"
                    break
        
        if(self.pdf == "NOSHEET"):
            print("Datasheet could not be determined for this device: " + self.name)
            
    def processPins(self):
        #{"TOP": [], "BOTTOM": [], "RESET": [], "BOOT": [], "PWR": [], "OSC": [], "OTHER": [], "PORT": {}}
        self.resetPins = []
        self.bootPins = []
        self.powerPins = []
        self.clockPins = []
        self.otherPins = []
        self.ports = {}
        
        self.leftPins = []
        self.rightPins = []
        self.topPins = []
        self.bottomPins = []
        
        # Classify pins
        for pin in self.pins:
            if ((pin.pintype == "I/O" or pin.pintype == "Clock") and pin.name.startswith("P")):
                port = pin.name[1]
                try:
                    self.ports[port][int(pin.name[2:])] = pin
                except KeyError:
                    self.ports[port] = {}
                    self.ports[port][int(pin.name[2:])] = pin
            elif (pin.pintype == "Clock"):
                self.clockPins.append(pin)  
            elif ((pin.pintype == "Power") or (pin.name.startswith("VREF"))):
                if(pin.name.startswith("VDD")):
                    self.topPins.append(pin)
                elif(pin.name.startswith("VSS")):
                    self.bottomPins.append(pin)
                else:
                    self.powerPins.append(pin)
            elif (pin.pintype == "Reset"):
                self.resetPins.append(pin)
            elif (pin.pintype == "Boot"):
                self.bootPins.append(pin)
            else:
                self.otherPins.append(pin)
        
        # Apply pins to sides
        leftGroups = [[]]
        rightGroups = [[]]
        
        if len(self.resetPins) > 0:
            leftGroups.append(self.resetPins)
        if len(self.bootPins) > 0:
            leftGroups.append(self.bootPins)
        if len(self.powerPins) > 0:
            leftGroups.append(self.powerPins)
        if len(self.clockPins) > 0:
            leftGroups.append(self.clockPins)
        if len(self.otherPins) > 0:
            leftGroups.append(self.otherPins)
        
        del leftGroups[0]

        leftSpace = 0
        rightSpace = 0
        
        for group in leftGroups:
            l = len(group)
            leftSpace += l + 1
            
        serviceSpace = leftSpace
                    
        portNames = sorted(self.ports.keys())

        for portname in portNames:
            port = self.ports[portname]
            pins = []
            for pinname in sorted(port.keys()):
                pins.append(port[pinname])
            l = len(pins)
            rightSpace += l + 1
            rightGroups.append(pins)
        
        del rightGroups[0]
                        
        maxSize = max(leftSpace, rightSpace)
        movedSpace = 0
        
        movedGroups = []
        
        while(True):
            groupToMove = rightGroups[-1]
            newLeftSpace = leftSpace + len(groupToMove) + 1
            newRightSpace = rightSpace - len(groupToMove) - 1
            newSize = max(newLeftSpace, newRightSpace)
            if newSize >= maxSize:
                break;
            maxSize = newSize
            leftSpace = newLeftSpace
            rightSpace = newRightSpace

            movedSpace += len(groupToMove) + 1
            
            movedGroups.append(groupToMove)
            rightGroups.pop()

        for group in movedGroups:
            i = 0
            for pin in group:
                pin.y = - (movedSpace - 1) + i
                i += 1
            movedSpace -= i + 1
            leftGroups.append(group)
            
        movedSpace = 0
        for group in reversed(rightGroups):
            movedSpace += len(group) + 1
            i = 0
            for pin in group:
                pin.y = - (movedSpace - 1) + i
                i += 1
            
        y = 0
        for group in leftGroups:
            for pin in group:
                if pin.placed:
                    continue
                if pin.y < 0:
                    pin.y = maxSize + pin.y - 1
                else:
                    pin.y = y
                pin.placed = True
                self.leftPins.append(pin)
                y += 1
            y += 1
            
        y = 0
        for group in rightGroups:
            for pin in group:
                if pin.placed:
                    continue
                if pin.y < 0:
                    pin.y = maxSize + pin.y - 1
                else:
                    pin.y = y
                pin.placed = True
                self.rightPins.append(pin)
                y += 1
            y += 1
            
        maxXSize = 0
        for i in range(maxSize):
            size = 0
            for pin in self.pins:
                if (pin.placed == True) and (int(pin.y) == i):
                    pin.createPintext(False)
                    size += len(pin.pintext)

            if (maxXSize < size):
                maxXSize = size
        
        topMaxLen = 0
        self.topPins = sorted(self.topPins, key=lambda p: p.name)
        topX = - int(len(self.topPins) / 2)
        for pin in self.topPins:
            pin.x = topX
            topX += 1
            pin.createPintext(False)
            if len(pin.pintext) > topMaxLen:
                topMaxLen = len(pin.pintext)
                
        bottomMaxLen = 0
        self.bottomPins = sorted(self.bottomPins, key=lambda p: p.name)
        bottomX = - int(len(self.bottomPins) / 2)
        for pin in self.bottomPins:
            pin.x = bottomX
            bottomX += 1
            pin.createPintext(False)
            if len(pin.pintext) > bottomMaxLen:
                bottomMaxLen = len(pin.pintext)
        
        self.yTopMargin = math.ceil((topMaxLen * 47 + 75) / 100)
        self.yBottomMargin = math.ceil((bottomMaxLen * 47 + 75) / 100)
                
        self.boxHeight = (maxSize - 2 + self.yTopMargin + self.yBottomMargin) * 100
        #self.boxHeight = math.floor(self.boxHeight / 100) * 100
        #if (self.boxHeight / 2) % 100 > 0:
        #    self.boxHeight += 100
            
        self.boxWidth = (maxXSize + 1) * 47 + 100
        self.boxWidth = math.floor(self.boxWidth / 100) * 100
        if (self.boxWidth / 2) % 100 > 0:
            self.boxWidth += 100
            
        #print(self.rightPins)

    def createComponent(self):
        self.processPins()
        
        # s contains the entire component in a single string
        if (len(self.pins) < 100):
            pinlength = 100
        else:
            pinlength = 200
            
        yOffset = math.ceil(self.boxHeight / 100 / 2) * 100
            
        s = ""
        s += "#\r\n"
        s += "# " + self.name.upper() + "\r\n"
        s += "#\r\n"
        s += "DEF " + self.name + " U 0 40 Y Y 1 L N\r\n"
        s += "F0 \"U\" " + str(round(- self.boxWidth / 2)) + " " + str(round(yOffset) + 25) + " 50 H V L B\r\n"
        s += "F1 \"" + self.name + "\" " + str(round(self.boxWidth / 2)) + " " + str(round(yOffset) + 25) + " 50 H V R B\r\n"
        s += "F2 \"" + self.package + "\" " + str(round(self.boxWidth / 2)) + " " + str(round(yOffset) - 25) + " 50 H V R T\r\n"
        s += "F3 \"~\" 0 0 50 H V C CNN\r\n"
        if (len(self.aliases) > 0):
            s += "ALIAS " + " ".join(self.aliases) + "\r\n"
        s += "DRAW\r\n"
        
        
        y = 0
        for pin in self.rightPins:
            pin.createPintext(True)
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(int(self.boxWidth / 2 + pinlength)) + " " + str(round(yOffset - (pin.y + self.yTopMargin) * 100)) + " " + str(pinlength) + " L 50 50 1 1 " + PIN_TYPES_MAPPING[pin.pintype] + "\r\n"
            y += 1
                
        for pin in self.leftPins:
            pin.createPintext(False)
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(int(- self.boxWidth / 2 - pinlength)) + " " + str(round(yOffset - (pin.y + self.yTopMargin) * 100)) + " " + str(pinlength) + " R 50 50 1 1 " + PIN_TYPES_MAPPING[pin.pintype] + "\r\n"
            
        for pin in self.topPins:    
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(int(pin.x * 100)) + " " + str(int(yOffset + pinlength)) + " " + str(pinlength) + " D 50 50 1 1 " + PIN_TYPES_MAPPING[pin.pintype] + "\r\n"
            
        for pin in self.bottomPins:
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(int(pin.x * 100)) + " " + str(int(yOffset - self.boxHeight - pinlength)) + " " + str(pinlength) + " U 50 50 1 1 " + PIN_TYPES_MAPPING[pin.pintype] + "\r\n"
        
        s += "S -" + str(round(self.boxWidth / 2)) + " " + str(int(yOffset - self.boxHeight)) + " " + str(int(self.boxWidth / 2)) + " " + str(int(yOffset)) + " 0 1 10 f\r\n"
        s += "ENDDRAW\r\n"
        s += "ENDDEF\r\n"

        self.componentstring = s
        
    def createDocu(self):
        pdfprefix = "http://www.st.com/st-web-ui/static/active/en/resource/technical/document/datasheet/"
        if(self.pdf == "NOSHEET"):
            pdfprefix = ""
            self.pdf = ""
        names = [self.name] + self.aliases
        s = ""
        for name in names:
            s += "$CMP " + name + "\r\n"
            s += "D Core: " + self.core + " Package: " + self.package + " Flash: " + self.flash + "KB Ram: " + self.ram + "KB "
            if self.freq:
                s += "Frequency: " + self.freq + "MHz "
            if self.voltage:
                s += "Voltage: " + self.voltage[0] + ".." + self.voltage[1] + "V "
            s += "IO-pins: " + self.io + "\r\n"
            s += "K " + " ".join([self.core, self.family, self.line]) + "\r\n"
            s += "F " + pdfprefix + self.pdf + "\r\n"   # TODO: Add docfiles to devices, maybe url to docfiles follows pattern?
            s += "$ENDCMP\r\n"
        self.docustring = s


def main():
    args = sys.argv
    
    if(not len(args) == 3 or args[1] == "help"):
        printHelp()
    elif(os.path.isdir(args[1]) and os.path.isdir(args[2])):

        lib = open("stm32.lib", "w")
        docu = open("stm32.dcm", "w")

        #TODO: Add date and time of file generation to header
        lib.write("EESchema-LIBRARY Version 2.3\r\n#encoding utf-8\r\n")
        docu.write("EESchema-DOCLIB  Version 2.0\r\n#\r\n")

        files = []
        for (dirpath, dirnames, filenames) in os.walk(args[2]):
            files.extend(filenames)
            break
        

        for pdffile in files:
            pdffile = os.path.join(args[2], pdffile)
            pdfparsedfile = pdffile + ".par"
            if(not os.path.isfile(pdfparsedfile) and pdffile.endswith(".pdf")):
                print("Converting: " + pdffile)
                os.system("pdf2txt.py -o " + pdfparsedfile + " " + pdffile)

        files = []
        for (dirpath, dirnames, filenames) in os.walk(args[1]):
            files.extend(filenames)
            break
        
        files.sort()

        for xmlfile in files:
            mcu = device(os.path.join(args[1], xmlfile), args[2])
            if(mcu.pdf != ""):
                lib.write(mcu.componentstring)
                docu.write(mcu.docustring)

        lib.write("#\r\n# End Library\r\n")
        lib.close()

        docu.write("#\r\n#End Doc Library")
        docu.close()
    else:
        printHelp()

def printHelp():
    print("Usage: main.py path/to/xmldir path/to/pdfdir \r\nDirectory should ONLY contain valid xml files, otherwise the result will be bogus.\r\nI haven't included any error checking, so good luck!")

if __name__ == "__main__":
    main()
