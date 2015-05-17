#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET
from lxml import etree
import os

class pin:
    def __init__(self, pinnumber, name, pintype):
        self.pinnumber = pinnumber
        self.name = name
        self.pintype = pintype
        self.altfunctions = []
        
class device:
    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
        self.name = ""
        self.package = ""
        self.pins = []

        self.readxml()

    def readxml(self):
        self.tree = etree.parse(self.xmlfile)
        self.root = self.tree.getroot()

        self.ns = {"a": self.root.nsmap[None]}  # F@#k you xml

        self.name = self.root.get("RefName")
        self.package = self.root.get("Package")

        for child in self.root.xpath("a:Pin",namespaces=self.ns):
            # Create object and read attributes
            newpin = pin(child.get("Position"), child.get("Name"), child.get("Type"))
            for signal in child.xpath("a:Signal",namespaces=self.ns):
                altfunction = signal.get("Name")
                if(not altfunction == "GPIO"):   # No need to add GPIO as alt function
                    newpin.altfunctions.append(altfunction)
            self.pins.append(newpin)

    def createComponent(self):
        # s contains the entire component in a single string
        s = ""





        self.componentstring = s
            

def main():
    args = sys.argv
    ns = "{http://mcd.rou.st.com/modules.php?name=mcu}"
    
    pins = []

    if(not len(args) == 2 or args[1] == "help"):
        printHelp()
    elif(os.path.isfile(args[1])):
        test = device(args[1])
        

    else:
        printHelp()
    



def printHelp():
    print("Usage: main.py path/to/file.xml")

if __name__ == "__main__":
    main()
