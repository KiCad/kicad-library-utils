#!/usr/bin/env python3

import sys,os,math
from lxml import etree

class pin:
    def __init__(self, pinnumber, name, pintype):
        self.pinnumber = pinnumber
        self.name = name
        self.pintype = pintype
        self.altfunctions = []
        self.drawn = False  # Whether this pin has already been included in the component or not

    def createPintext(self):
        s = ""
        for alt in self.altfunctions:
            s += alt + "/"
        s += self.name
        self.pintext = s.replace(" ","")

class device:
    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
        self.name = ""
        self.package = ""
        self.pins = []

        self.readxml()
        self.createComponent()
        self.createDocu()

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
            newpin.createPintext()  # Have the pins generate their text
            self.pins.append(newpin)
        
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
            self.freq = "--"    # Some devices don't have a frequency specification... thanks obama!
        self.ram = self.root.xpath("a:Ram", namespaces=self.ns)[0].text
        self.io = self.root.xpath("a:IONb", namespaces=self.ns)[0].text
        self.flash = self.root.xpath("a:Flash", namespaces=self.ns)[0].text
        
        self.voltage = [self.root.xpath("a:Voltage", namespaces=self.ns)[0].get("Min", default="--"), self.root.xpath("a:Voltage", namespaces=self.ns)[0].get("Max", default="--")]

    def createComponent(self):
        # s contains the entire component in a single string
        pinlength = 150

        ports = {}
        portpins = {}
        pincount = 0
        portcount = 0
        maxleftstringlen = 0
        # Count amount of different Ports and how many I/O pins they contain
        for pin in self.pins:
            if(pin.pintype == "I/O" and len(pin.name) <= 4 and pin.name.startswith("P")):    # Avoid counting oscillator pins
                pincount += 1
                port = pin.name[1]
                try:
                    ports[port] += 1    # Increment pincount for this port
                except KeyError:
                    ports[port] = 1     # Key doesn't yet exist, create it
                    portcount += 1
                    portpins[port] = {} # Same as above
                portpins[port][int(pin.name[2:])] = pin
            elif(pin.pintype == "I/O" and len(pin.name) > 4):
                maxleftstringlen = max(maxleftstringlen, len(pin.pintext))
       
        maxstringlen = 0
        powerpins = {"VDD": {}, "VSS": {}}
        for pin in self.pins:
            if(pin.pintype == "Power"):
                maxstringlen = max(maxstringlen, len(pin.name))
                if(pin.name.startswith("VDD")):
                    powerpins["VDD"][pin.pinnumber] = pin
                elif(pin.name.startswith("VSS")):
                    powerpins["VSS"][pin.pinnumber] = pin
        
        padding = math.ceil(round(maxstringlen*50)/100)*100 + 100   # This will add padding on top of the horizontal pins for the vertical pins
        boxheight = (pincount - 1) * 100 + (portcount - 1) * 100 + padding * 2  # height in mils 
        
        maxstringlen = 0
        for pin in self.pins:
            maxstringlen = max(maxstringlen, len(pin.pintext))

        boxwidth = maxstringlen * 48 + maxleftstringlen * 48
        
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
        # Start to iterate through ports alphabetically
        positioncounter = 0
        portkeys = sorted(list(ports.keys()))
        for port in portkeys:
            pinnumbers = sorted(list(portpins[port].keys()))
            for pinnumber in pinnumbers:
                pin = portpins[port][pinnumber]
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(boxwidth/2 + pinlength)) + " " + str(round(boxheight/2 - positioncounter*100 - padding)) + " " + str(pinlength) + " L 50 50 1 1 I\r\n"
                positioncounter += 1
                pin.drawn = True
            positioncounter += 1    # Create gap between 2 ports
        
        # Draw VDD pins on top of component
        vddkeys = sorted(list(powerpins["VDD"].keys()))
        counter = 0
        for key in vddkeys:
            pin = powerpins["VDD"][key]
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-((len(vddkeys)-1) * 100)/2 + counter * 100)) + " " + str(round(boxheight/2) + pinlength) + " " + str(pinlength) + " D 50 50 1 1 I\r\n"
            counter += 1
            pin.drawn = True

        # Draw VSS pins on bottom of component
        vsskeys = sorted(list(powerpins["VSS"].keys()))
        counter = 0
        for key in vsskeys:
            pin = powerpins["VSS"][key]
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-((len(vsskeys)-1) * 100)/2 + counter * 100)) + " " + str(-round(boxheight/2) - pinlength) + " " + str(pinlength) + " U 50 50 1 1 I\r\n"
            counter += 1
            pin.drawn = True

        # Draw all remaining pins on left hand side
        leftpincounter = 0

        # Draw Reset pin
        for pin in self.pins:
            if(pin.pintype == "Reset"):
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(boxheight/2) - leftpincounter * 100 - padding) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
                pin.drawn = True
                leftpincounter += 1
        leftpincounter += 1 # Create gap between Reset and Boot
        
        # Draw boot pin
        for pin in self.pins:
            if(pin.pintype == "Boot"):
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(boxheight/2) - leftpincounter * 100 - padding) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
                pin.drawn = True
                leftpincounter += 1
        leftpincounter += 1

        # Draw remaining power pins
        for pin in self.pins:
            if(pin.pintype == "Power" and pin.drawn == False):
                s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(boxheight/2) - leftpincounter * 100 - padding) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
                pin.drawn = True
                leftpincounter += 1

        # Remaining pins
        remainingpins = []
        for pin in self.pins:
            if(not pin.drawn):
                remainingpins.append(pin)
        
        leftpincounter = 0
        remainingpins.sort(key = lambda x: x.name)
        for pin in remainingpins:
            s += "X " + pin.pintext + " " + str(pin.pinnumber) + " " + str(round(-boxwidth/2 - pinlength)) + " " + str(round(-leftpincounter * 100)) + " " + str(pinlength) + " R 50 50 1 1 I\r\n"
            leftpincounter += 1

        s += "S -" + str(round(boxwidth/2)) + " -" + str(round(boxheight/2)) + " " + str(round(boxwidth/2)) + " " + str(round(boxheight/2)) + " 0 1 10 f\r\n"
        s += "ENDDRAW\r\n"
        s += "ENDDEF\r\n"

        self.componentstring = s

    def createDocu(self):
        
        s = ""
        s += "$CMP " + self.name.upper() + "\r\n"
        s += "D Core: " + self.core + " Flash: " + self.flash + "kB Ram: " + self.ram + "kB Frequency: " + self.freq + "MHz Voltage: " + self.voltage[0] + ".." + self.voltage[1] + "V IO-pins: " + self.io + "\r\n"
        s += "K " + " ".join([self.core, self.family, self.line]) + "\r\n"
        s += "F \r\n"   # TODO: Add docfiles to devices, maybe url to docfiles follows pattern?
        s += "$ENDCMP\r\n"
        self.docustring = s


def main():
    args = sys.argv
    
    if(not len(args) == 2 or args[1] == "help"):
        printHelp()
    elif(os.path.isdir(args[1])):

        lib = open("stm32.lib", "w")
        docu = open("stm32.dcm", "w")

        #TODO: Add date and time of file generation to header
        lib.write("EESchema-LIBRARY Version 2.3\r\n#encoding utf-8\r\n")
        docu.write("EESchema-DOCLIB  Version 2.0\r\n#\r\n")

        files = []
        for (dirpath, dirnames, filenames) in os.walk(args[1]):
            files.extend(filenames)
            break

        for xmlfile in files:
            mcu = device(os.path.join(args[1], xmlfile))
            lib.write(mcu.componentstring)
            docu.write(mcu.docustring)

        lib.write("#\r\n# End Library\r\n")
        lib.close()

        docu.write("#\r\n#End Doc Library")
        docu.close()
    else:
        printHelp()

def printHelp():
    print("Usage: main.py path/to/dir\r\nDirectory should ONLY contain valid xml files, otherwise the result will be bogus.\r\nI haven't included any error checking, so good luck!")

if __name__ == "__main__":
    main()
