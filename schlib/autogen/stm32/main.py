#!/usr/bin/env python3

import argparse
import math
import os
import re

from lxml import etree

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

POWER_PAD_FIX_PACKAGES = {"UFQFPN28", "UFQFPN32", "UFQFPN48", "VFQFPN36"}

FOOTPRINT_MAPPING = {
    # No footprint "EWLCSP49": "",
    # No footprint "EWLCSP66": "",
    # No footprint "LFBGA100": "",
    # No footprint "LFBGA144": "",
    "LQFP32": "Package_QFP:LQFP-32_7x7mm_P0.8mm",
    "LQFP48": "Package_QFP:LQFP-48_7x7mm_P0.5mm",
    "LQFP64": "Package_QFP:LQFP-64_10x10mm_P0.5mm",
    "LQFP100": "Package_QFP:LQFP-100_14x14mm_P0.5mm",
    "LQFP144": "Package_QFP:LQFP-144_20x20mm_P0.5mm",
    "LQFP176": "Package_QFP:LQFP-176_24x24mm_P0.5mm",
    "LQFP208": "Package_QFP:LQFP-208_28x28mm_P0.5mm",
    # Closest footprint has wrong pad dimensions, risky for BGA "TFBGA64": "",
    # No footprint "TFBGA100": "",
    # No footprint "TFBGA216": "",
    # No footprint "TFBGA240": "",
    "TSSOP14": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
    "TSSOP20": "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
    # Closest footprint has wrong pad dimensions, risky for BGA "UFBGA64": "",
    # No footprint "UFBGA100": "",
    "UFBGA132": "Package_BGA:UFBGA-132_7x7mm_P0.5mm",
    # ST uses this name for two sizes of BGA "UFBGA144": "",
    # No footprint "UFBGA169": "",
    # No footprint "UFBGA176": "",
    "UFQFPN20": "Package_DFN_QFN:ST_UFQFPN-20_3x3mm_P0.5mm",
    # No footprint "UFQFPN28": "",
    "UFQFPN32": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
    "UFQFPN48": "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm",
    "VFQFPN36": "Package_DFN_QFN:QFN-36-1EP_6x6mm_P0.5mm_EP3.7x3.7mm",
    # No footprint "WLCSP25": "",
    # No footprint "WLCSP36": "",
    # No footprint "WLCSP49": "",
    # No footprint "WLCSP63": "",
    # No footprint "WLCSP64": "",
    # No footprint "WLCSP66": "",
    # No footprint "WLCSP72": "",
    # No footprint "WLCSP81": "",
    # No footprint "WLCSP90": "",
    # No footprint "WLCSP100": "",
    # No footprint "WLCSP104": "",
    # No footprint "WLCSP143": "",
    # No footprint "WLCSP144": "",
    # No footprint "WLCSP168": "",
    # No footprint "WLCSP180": ""
}

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
        self.altNames = []
        self.pintype = pintype
        self.altfunctions = altf
        self.drawn = False  # Whether this pin has already been included in the component or not
        self.x = 0;
        self.y = 0;
        self.placed = False

    def createPintext(self, left):
        if (left):
            if (self.name == ""):
                s = (self.altNames + self.altfunctions)[0]
            else:
                s = self.name
        else:
            if (self.name == ""):
                s = (self.altNames + self.altfunctions)[0]
            else:
                s = self.name
        self.pintext = s.replace(" ","")

class device:
    def __init__(self, xmlfile, pdfdir):
        print(xmlfile)
        self.xmlfile = xmlfile
        self.pdfdir = pdfdir
        self.name = ""
        self.package = ""
        self.footprint = ""
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

        # Get the footprint for this package
        try:
            self.footprint = FOOTPRINT_MAPPING[self.package]
        except KeyError:
            self.footprint = self.package

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

        self.hasPowerPad = False

        if self.root.get("HasPowerPad") == "true":
            self.hasPowerPad = True
        else:
            if self.package in POWER_PAD_FIX_PACKAGES:
                print("Absent powerpad detected in part " + self.name)
                self.hasPowerPad = True

        if(self.hasPowerPad == True):    # Special case for the thermal pad
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
        self.ram = [r.text for r in self.root.xpath("a:Ram", namespaces=self.ns)]
        self.io = self.root.xpath("a:IONb", namespaces=self.ns)[0].text
        self.flash = [f.text for f in self.root.xpath("a:Flash", namespaces=self.ns)]
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
    
    def runDRC(self):
        pinNumMap = {}
        removePins = []
        for pin in self.pins:
            if pin.pinnumber in pinNumMap:
                print("Duplicated pin " + str(pin.pinnumber) + " in part " + self.name + ", merging")
                mergedPin = pinNumMap[pin.pinnumber]
                mergedPin.altNames.append(pin.name)
                mergedPin.altfunctions += pin.altfunctions
                removePins.append(pin)
            pinNumMap[pin.pinnumber] = pin
            
        for pin in removePins:
            self.pins.remove(pin)
    
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
                pin_num = int(re.findall('\d+', pin.name)[0])
                try:
                    self.ports[port][pin_num] = pin
                except KeyError:
                    self.ports[port] = {}
                    self.ports[port][pin_num] = pin
            elif (pin.pintype == "Clock"):
                self.clockPins.append(pin)  
            elif ((pin.pintype == "Power") or (pin.name.startswith("VREF"))):
                if pin.name.startswith("VDD") or pin.name.startswith("VBAT"):
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
            
        self.boxWidth = max((maxXSize + 1) * 47 + 200,
                            100*(len(self.topPins) + 1),
                            100*(len(self.bottomPins) + 1))
        self.boxWidth = math.floor(self.boxWidth / 100) * 100
        if (self.boxWidth / 2) % 100 > 0:
            self.boxWidth += 100
            
        #print(self.rightPins)

    def createComponent(self):
        self.runDRC()
        self.processPins()
        
        # s contains the entire component in a single string
        if (len(self.pins) < 100):
            pinlength = 100
        else:
            pinlength = 200
            
        yOffset = math.ceil(self.boxHeight / 100 / 2) * 100
            
        s = []
        s.append("#\n")
        s.append(f"# {self.name.upper()}\n")
        s.append("#\n")
        s.append(f"DEF {self.name} U 0 40 Y Y 1 L N\n")
        s.append(f'F0 "U" {str(round(- self.boxWidth / 2))} '
                 f'{str(round(yOffset) + 25)} 50 H V L B\n')
        s.append(f'F1 "{self.name}" {str(round(self.boxWidth / 2))} '
                 f'{str(round(yOffset) + 25)} 50 H V L B\n')
        s.append(f'F2 "{self.footprint}" {str(round(self.boxWidth / 2))} '
                 f'{str(round(yOffset) - 25)} 50 H I R T\n')
        s.append('F3 "" 0 0 50 H I C CNN\n')
        if (len(self.aliases) > 0):
            s.append(f'ALIAS {" ".join(self.aliases)}\n')
        s.append("DRAW\n")
        
        
        for pin in self.rightPins:
            pin.createPintext(True)
            s.append(f"X {pin.pintext} {str(pin.pinnumber)} "
                     f"{str(int(self.boxWidth / 2 + pinlength))} "
                     f"{str(round(yOffset - (pin.y + self.yTopMargin) * 100))}"
                     f" {str(pinlength)} L 50 50 1 1 "
                     f"{PIN_TYPES_MAPPING[pin.pintype]}\n")

        for pin in self.leftPins:
            pin.createPintext(False)
            s.append(f"X {pin.pintext} {str(pin.pinnumber)} "
                     f"{str(int(-self.boxWidth / 2 - pinlength))} "
                     f"{str(round(yOffset - (pin.y + self.yTopMargin) * 100))}"
                     f" {str(pinlength)} R 50 50 1 1 "
                     f"{PIN_TYPES_MAPPING[pin.pintype]}\n")

        for pin in self.topPins:
            s.append(f"X {pin.pintext} {str(pin.pinnumber)} "
                     f"{str(int(pin.x * 100))} {str(int(yOffset + pinlength))}"
                     f" {str(pinlength)} D 50 50 1 1 "
                     f"{PIN_TYPES_MAPPING[pin.pintype]}\n")

        for pin in self.bottomPins:
            s.append(f"X {pin.pintext} {str(pin.pinnumber)} "
                     f"{str(int(pin.x * 100))} "
                     f"{str(int(yOffset - self.boxHeight - pinlength))} "
                     f"{str(pinlength)} U 50 50 1 1 "
                     f"{PIN_TYPES_MAPPING[pin.pintype]}\n")
        
        s.append(f"S -{str(round(self.boxWidth / 2))} "
                 f"{str(int(yOffset - self.boxHeight))} "
                 f"{str(int(self.boxWidth / 2))} "
                 f"{str(int(yOffset))} 0 1 10 f\n")
        s.append("ENDDRAW\n")
        s.append("ENDDEF\n")

        self.componentstring = "".join(s)
        
    def createDocu(self):
        pdfprefix = "http://www.st.com/st-web-ui/static/active/en/resource/technical/document/datasheet/"
        if(self.pdf == "NOSHEET"):
            pdfprefix = ""
            self.pdf = ""
        names = [self.name] + self.aliases
        s = []
        for i, name in enumerate(names):
            f = 0 if len(self.flash) == 1 else i
            r = 0 if len(self.ram) == 1 else i
            s.append(f"$CMP {name}\n")
            s.append(f"D Core: {self.core} Package: {self.package} Flash: "
                     f"{self.flash[f]}KB Ram: {self.ram[r]}KB ")
            if self.freq:
                s.append(f"Frequency: {self.freq}MHz ")
            if self.voltage:
                s.append(f"Voltage: {self.voltage[0]}..{self.voltage[1]}V ")
            s.append(f"IO-pins: {self.io}\n")
            s.append(f"K {self.core} {self.family} {self.line}\n")
            s.append(f"F {pdfprefix}{self.pdf}\n")   # TODO: Add docfiles to devices, maybe url to docfiles follows pattern?
            s.append("$ENDCMP\n")
            s.append("#\n")
        self.docustring = "".join(s)


def main():
    parser = argparse.ArgumentParser(
            description='Generator for STM32 microcontroller symbols')
    parser.add_argument('xmldir',
            help='Directory containing ONLY valid STM32 XML files')
    parser.add_argument('pdfdir',
            help='Directory containing STM32 datasheet PDFs')

    args = parser.parse_args()

    if not os.path.isdir(args.xmldir) or not os.path.isdir(args.pdfdir):
        parser.error("xmldir and pdfdir must be directories")

    libname_format = "MCU_ST_{}.{}"

    files = []
    for (dirpath, dirnames, filenames) in os.walk(args.pdfdir):
        files.extend(filenames)
        break

    for pdffile in files:
        pdffile = os.path.join(args.pdfdir, pdffile)
        pdfparsedfile = pdffile + ".par"
        if(not os.path.isfile(pdfparsedfile) and pdffile.endswith(".pdf")):
            print("Converting: " + pdffile)
            os.system("pdf2txt.py -o " + pdfparsedfile + " " + pdffile)

    files = []
    for (dirpath, dirnames, filenames) in os.walk(args.xmldir):
        files.extend(filenames)
        break

    files.sort()

    devices = {}

    for xmlfile in files:
        mcu = device(os.path.join(args.xmldir, xmlfile), args.pdfdir)
        if mcu.family not in devices:
            devices[mcu.family] = []
        devices[mcu.family].append(mcu)

    for family, mcus in devices.items():
        print(family, len(mcus))
        # TODO: Add date and time of file generation to header
        with open(libname_format.format(family, "lib"), "w") as lib:
            lib.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
            for mcu in mcus:
                if mcu.pdf != "":
                    lib.write(mcu.componentstring)
            lib.write("#\n# End Library\n")

        with open(libname_format.format(family, "dcm"), "w") as dcm:
            dcm.write("EESchema-DOCLIB  Version 2.0\n#\n")
            for mcu in mcus:
                if mcu.pdf != "":
                    dcm.write(mcu.docustring)
            dcm.write("#\n#End Doc Library")

if __name__ == "__main__":
    main()
