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

        self.readxml()
        #self.readpdf()
        self.createComponent()
        #self.createDocu()

    def readxml(self):
        self.tree = etree.parse(self.xmlfile)
        self.root = self.tree.getroot()

        self.ns = {"a": self.root.nsmap[None]}  # I hate XML

        self.name = self.root.get("RefName")
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
            self.pins.append(newpin)
        if(self.root.get("HasPowerPad") == "true"):    # Special case for the thermal pad
            powerpadpin = pin("Th", "VSS/TH", "Power")
            self.pins.append(powerpadpin)

        
        if(not self.bga):
            for apin in self.pins:
                if(not apin.name == "VSS/TH"):
                    apin.pinnumber = int(apin.pinnumber)

        # Parse information for documentation
        self.core = self.root.xpath("a:Core", namespaces=self.ns)[0].text
        self.family = self.root.get("Family")
        self.line = self.root.get("Line")
        try:
            self.freq = self.root.xpath("a:Frequency", namespaces=self.ns)[0].text
        except:
            self.freq = "--"    # Some devices don't have a frequency specification... thanks obama!
        self.ram = self.root.xpath("a:Ram", namespaces=self.ns)[0].text
        self.io = self.root.xpath("a:IONb", namespaces=self.ns)[0].text
        self.flash = self.root.xpath("a:Flash", namespaces=self.ns)[0].text
        try:
            self.voltage = [self.root.xpath("a:Voltage", namespaces=self.ns)[0].get("Min", default="--"), self.root.xpath("a:Voltage", namespaces=self.ns)[0].get("Max", default="--")]
        except:
            self.voltage = ["--", "--"] # Some devices don't have a voltage specification also

    def readpdf(self):
        self.pdf = "NOSHEET"
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.pdfdir):
            files.extend(filenames)
            break

        s = self.name
        if("(" in s and ")" in s):
            paren = s[s.find("(")+1:s.find(")")]    # Get device options contained in parenthesis
            s = s.replace("("+paren+")","o")    # Replace the parenthesis with a lower case 'o'
            paren = paren.split("-")    # Paren contains different options

        #print("NEW: " + s)
        candidatestring = {}
        for pdf in files:
            if(pdf.endswith(".pdf.par")):   # Find all processed PDF files and open them for evaluation
                p = open(os.path.join(self.pdfdir, pdf), "r")
                for line in p:
                    if(line.find(s[:9]) >= 0):
                        candidatenames = line.rstrip().translate(str.maketrans(","," ")).split()    # Remove newline and commas and then split string
                        for candidatename in candidatenames:
                            candidatestring[candidatename] = pdf    # Associate file with every device name
                    if(not line.startswith("STM32")):   # Assume that the device names are always at the beginning of file
                        break
        #print(candidatestring)  # TODO: CONTINUE HERE!!!!
        keystokeep = []
        for key in candidatestring:
            pdfstr = candidatestring[key]
            indices = [m.start() for m in re.finditer('x', key)]
            tempname = list(s)
            tempkey = list(key)
            for ind in indices:
                tempname[ind] = "r"
                tempkey[ind] = "r"
            mods = "".join(tempname).replace("r","")
            modkey = "".join(tempkey).replace("r","")
            #print(s + " " + key)
            #print(mods + " " + modkey)

            if(mods.find("o") > 0):
                for option in paren:
                    temps = mods.replace("o",option)
                    #print(temps)
                    if(temps.startswith(modkey)):
                        keystokeep.append(key)
            elif(mods.startswith(modkey)):
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
                    self.pdf = "NOSHEET"
                    break
        
        if(self.pdf == "NOSHEET"):
            print("Datasheet could not be determined for this device: " + self.name)


    def createComponent(self):
        # s contains the entire component in a single string
        if (len(self.pins) < 100):
            pinlength = 100
        else:
            pinlength = 200

        ports = {}
        portpins = {}
        pincount = 0
        portcount = 0
        maxleftstringlen = 0
        # Count amount of different Ports and how many I/O pins they contain
        for pin in self.pins:
            if(pin.pintype == "I/O" and pin.name.startswith("P")):    # Avoid counting oscillator pins
                pincount += 1
                port = pin.name[1]
                try:
                    ports[port] += 1    # Increment pincount for this port
                except KeyError:
                    ports[port] = 1     # Key doesn't yet exist, create it
                    portcount += 1
                    portpins[port] = {} # Same as above
                portpins[port][int(pin.name[2:])] = pin

        portkeys = sorted(list(ports.keys()))

        leftportcount = 0
        rightportcount = 0
        leftpincount = 0
        rightpincount = 0

        for port in reversed(portkeys):
            rightportcount += 1
            rightpincount += ports[port]
            if (rightpincount >= int((pincount + 16) / 2)):
                break;

        leftportcount = portcount - rightportcount
        leftpincount = pincount - rightpincount

        maxstringlen = 0
        powerpins = {"VDD": {}, "VSS": {}}
        for pin in self.pins:
            if(pin.pintype == "Power"):
                pin.createPintext(False)
                maxstringlen = max(maxstringlen, len(pin.name))
                if(pin.name.startswith("VDD")):
                    powerpins["VDD"][pin.pinnumber] = pin
                elif(pin.name.startswith("VSS")):
                    powerpins["VSS"][pin.pinnumber] = pin
        
        padding = math.ceil(round(maxstringlen*50)/100)*100 + 100   # This will add padding on top of the horizontal pins for the vertical pins
        porth = max(leftpincount + leftportcount + 16, rightpincount + rightportcount)
        boxheight = porth * 100 + padding * 2  # height in mils 
        if((boxheight/2)%100 > 0):
            boxheight += 100

        maxrightstringlen = 0
        maxleftstringlen = 0

        i = 0
        for port in portkeys:
            for pin in portpins[port]:
                if (i >= leftportcount):
                    portpins[port][pin].createPintext(True)
                    maxrightstringlen = max(maxrightstringlen, len(portpins[port][pin].pintext))
                else:
                    portpins[port][pin].createPintext(False)
                    maxleftstringlen = max(maxleftstringlen, len(portpins[port][pin].pintext))
            i = i + 1

        for pin in self.pins:
            if(pin.pintype == "Clock"):
                pin.createPintext(False)
                maxleftstringlen = max(maxleftstringlen, len(pin.pintext))

        boxwidth = maxrightstringlen * 48 + maxleftstringlen * 48
        boxwidth = math.floor(boxwidth/100)*100 # Round to 100
        if((boxwidth/2)%100 > 0):
            boxwidth += 100
        
        s = ""
        s += "#\r\n"
        s += "# " + self.name.upper() + "\r\n"
        s += "#\r\n"
        s += "DEF " + self.name + " U 0 40 Y Y 1 L N\r\n"
        s += "F0 \"U\" " + str(round(-boxwidth/2)) + " " + str(round(boxheight/2) + 25) + " 50 H V L B\r\n"
        s += "F1 \"" + self.name + "\" " + str(round(boxwidth/2)) + " " + str(round(boxheight/2) + 25) + " 50 H V R B\r\n"
        s += "F2 \"" + self.package + "\" " + str(round(boxwidth/2)) + " " + str(round(boxheight/2) - 25) + " 50 H V R T\r\n"
        s += "F3 \"~\" 0 0 50 H V C CNN\r\n"
        s += "DRAW\r\n"
        # Start drawing rectangles and pins

        # Draw right side ports in bottom-top order, starting from bottom
        portcounter = 0
        portposition = 0
        positioncounter = 0
        rightportkeys =  portkeys[leftportcount:]
        for port in rightportkeys:
            pinnumbers = sorted(list(portpins[port].keys()))
            if (portcounter == 0):
                portposition = len(pinnumbers)
            elif (portcounter < leftportcount):
                portposition += 17
            else:
                portposition += len(pinnumbers) + 1
            positioncounter = 0
            for pinnumber in pinnumbers:
                pin = portpins[port][pinnumber]
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(boxwidth/2 + pinlength)) + " " + str(round(-boxheight/2 + (portposition - positioncounter)*100 + padding)) + " " + str(pinlength) + " L 50 50 1 1 I\r\n"
                positioncounter += 1
                pin.drawn = True
            portcounter += 1

        # Draw left side ports in top-button order, starting from bottom
        portcounter = 0
        portposition = 0
        leftportkeys = reversed(portkeys[0:leftportcount])
        for port in leftportkeys:
            pinnumbers = sorted(list(portpins[port].keys()))
            if (portcounter == 0):
                portposition = len(pinnumbers)
            elif (portcounter < rightportcount):
                portposition += 17
            else:
                portposition += len(pinnumbers) + 1
            positioncounter = 0
            for pinnumber in pinnumbers:
                pin = portpins[port][pinnumber]
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(-boxheight/2 + (portposition - positioncounter)*100 + padding)) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
                positioncounter += 1
                pin.drawn = True
            portcounter += 1
        
        # Draw VDD pins on top of component
        vddkeys = list(powerpins["VDD"].keys())
        vddvalues = []
        for pin in list(powerpins["VDD"].values()):
            vddvalues.append(pin.name)
        vddvalues, vddkeys = zip(*sorted(zip(vddvalues,vddkeys)))
        counter = 0
        for key in vddkeys:
            pin = powerpins["VDD"][key]
            offset = 50
            if(len(vddkeys)%2):
                offset = 0
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-((len(vddkeys)-1) * 100)/2 + counter * 100 + offset)) + " " + str(round(boxheight/2) + pinlength) + " " + str(pinlength) + " D 50 50 1 1 I\r\n"
            counter += 1
            pin.drawn = True

        # Draw VSS pins on bottom of component
        vsskeys = list(powerpins["VSS"].keys())
        vssvalues = []
        for pin in list(powerpins["VSS"].values()):
            vssvalues.append(pin.name)
        if len(vsskeys) > 0: # Some packages (like UFQFPN32) has no dedicated VSS pins, only bottom pad
            vssvalues, vsskeys = zip(*sorted(zip(vssvalues,vsskeys)))
        counter = 0
        for key in vsskeys:
            pin = powerpins["VSS"][key]
            offset = 50
            if(len(vsskeys)%2):
                offset = 0
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-((len(vsskeys)-1) * 100)/2 + counter * 100 + offset)) + " " + str(-round(boxheight/2) - pinlength) + " " + str(pinlength) + " U 50 50 1 1 I\r\n"
            counter += 1
            pin.drawn = True

        # Draw all remaining pins on left hand side
        leftpincounter = 0

        # Draw Reset pin
        for pin in self.pins:
            if(pin.pintype == "Reset"):
                pin.createPintext(False)
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(boxheight/2) - leftpincounter * 100 - padding) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
                pin.drawn = True
                leftpincounter += 1
        leftpincounter += 1 # Create gap between Reset and Boot
        
        # Draw boot pin
        for pin in self.pins:
            if(pin.pintype == "Boot"):
                pin.createPintext(False)
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(boxheight/2) - leftpincounter * 100 - padding) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
                pin.drawn = True
                leftpincounter += 1
        leftpincounter += 1

        # Draw remaining power pins
        for pin in self.pins:
            if(pin.pintype == "Power" and pin.drawn == False):
                pin.createPintext(False)
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(boxheight/2) - leftpincounter * 100 - padding) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
                pin.drawn = True
                leftpincounter += 1
        leftpincounter += 1

        # Remaining pins
        remainingpins = []
        for pin in self.pins:
            if(not pin.drawn):
                remainingpins.append(pin)
        
        remainingpins.sort(key = lambda x: x.name)
        for pin in remainingpins:
            pin.createPintext(False)
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(boxheight/2) - leftpincounter * 100 - padding) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
            leftpincounter += 1

        s += "S -" + str(round(boxwidth/2)) + " -" + str(round(boxheight/2)) + " " + str(round(boxwidth/2)) + " " + str(round(boxheight/2)) + " 0 1 10 f\r\n"
        s += "ENDDRAW\r\n"
        s += "ENDDEF\r\n"

        self.componentstring = s

    def createDocu(self):
        pdfprefix = "http://www.st.com/st-web-ui/static/active/en/resource/technical/document/datasheet/"
        if(self.pdf == "NOSHEET"):
            pdfprefix = ""
            self.pdf = ""
        s = ""
        s += "$CMP " + self.name.upper() + "\r\n"
        s += "D Core: " + self.core + " Package: " + self.package + " Flash: " + self.flash + "kB Ram: " + self.ram + "kB Frequency: " + self.freq + "MHz Voltage: " + self.voltage[0] + ".." + self.voltage[1] + "V IO-pins: " + self.io + "\r\n"
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
        #docu = open("stm32.dcm", "w")

        #TODO: Add date and time of file generation to header
        lib.write("EESchema-LIBRARY Version 2.3\r\n#encoding utf-8\r\n")
        #docu.write("EESchema-DOCLIB  Version 2.0\r\n#\r\n")

        #files = []
        #for (dirpath, dirnames, filenames) in os.walk(args[2]):
        #    files.extend(filenames)
        #    break
        

        #for pdffile in files:
        #    pdffile = os.path.join(args[2], pdffile)
        #    pdfparsedfile = pdffile + ".par"
        #    if(not os.path.isfile(pdfparsedfile) and pdffile.endswith(".pdf")):
        #        print("Converting: " + pdffile)
        #        os.system("pdf2txt.py -o " + pdfparsedfile + " " + pdffile)

        files = []
        for (dirpath, dirnames, filenames) in os.walk(args[1]):
            files.extend(filenames)
            break

        for xmlfile in files:
            mcu = device(os.path.join(args[1], xmlfile), args[2])
            lib.write(mcu.componentstring)
        #    docu.write(mcu.docustring)

        lib.write("#\r\n# End Library\r\n")
        lib.close()

        #docu.write("#\r\n#End Doc Library")
        #docu.close()
    else:
        printHelp()

def printHelp():
    print("Usage: main.py path/to/xmldir path/to/pdfdir \r\nDirectory should ONLY contain valid xml files, otherwise the result will be bogus.\r\nI haven't included any error checking, so good luck!")

if __name__ == "__main__":
    main()
