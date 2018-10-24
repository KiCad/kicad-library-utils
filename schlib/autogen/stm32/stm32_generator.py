#!/usr/bin/env python3

import argparse
import logging
import math
import os
import re
import sys

from lxml import etree

sys.path.append(os.path.join(sys.path[0],'..'))
from KiCadSymbolGenerator import *


class DataPin:
    _PIN_TYPES_MAPPING = {
        "Power": DrawingPin.PinElectricalType.EL_TYPE_POWER_INPUT,
        "I/O": DrawingPin.PinElectricalType.EL_TYPE_BIDIR,
        "Reset": DrawingPin.PinElectricalType.EL_TYPE_INPUT,
        "Boot": DrawingPin.PinElectricalType.EL_TYPE_INPUT,
        "MonoIO": DrawingPin.PinElectricalType.EL_TYPE_BIDIR,
        "NC": DrawingPin.PinElectricalType.EL_TYPE_NC,
        "Clock": DrawingPin.PinElectricalType.EL_TYPE_INPUT
    }

    def __init__(self, number, name, pintype):
        self.num = number
        self.name = name
        self.pintype = pintype

    def to_drawing_pin(self, **kwargs):
        # Get the el_type for the DrawingPin
        el_type = DataPin._PIN_TYPES_MAPPING[self.pintype]
        # Get visibility based on el_type
        if el_type == DrawingPin.PinElectricalType.EL_TYPE_NC:
            visibility = DrawingPin.PinVisibility.INVISIBLE
        else:
            visibility = DrawingPin.PinVisibility.VISIBLE
        # Make the DrawingPin
        return DrawingPin(Point(0, 0), self.num, name=self.name,
                el_type=el_type, visibility=visibility, **kwargs)


class Device:
    _name_search = re.compile(r"^(.+)\((.+)\)(.+)$")
    _number_findall = re.compile(r"\d+")
    _pincount_search = re.compile(r"^[a-zA-Z]+([0-9]+)$")
    _pinname_split = re.compile('[ /-]+')
    _pkgname_sub = re.compile(r"([a-zA-Z]+)([0-9]+)(-.*|)")

    _SPECIAL_PIN_MAPPING = {
        "PC14OSC32_IN": ["PC14"],
        "PC15OSC32_OUT": ["PC15"],
        "PF11BOOT0": ["PF11"],
        "OSC_IN": [""],
        "OSC_OUT": [""],
        "VREF-": ["VREF-"],
        "VREFSD-": ["VREFSD-"]
    }
    _SPECIAL_TYPES_MAPPING = {
        "RCC_OSC_IN": "Clock",
        "RCC_OSC_OUT": "Clock"
    }
    _POWER_PAD_FIX_PACKAGES = {
        "UFQFPN32",
        "UFQFPN48",
        "VFQFPN36"
    }
    _FOOTPRINT_MAPPING = {
        "EWLCSP49-DIE447": "Package_CSP:ST_WLCSP-49_Die447",
        "EWLCSP66-DIE411": "Package_CSP:ST_WLCSP-66_Die411",
        "LFBGA100": "Package_BGA:LFBGA-100_10x10mm_Layout10x10_P0.8mm",
        "LFBGA144": "Package_BGA:LFBGA-144_10x10mm_Layout12x12_P0.8mm",
        "LQFP32": "Package_QFP:LQFP-32_7x7mm_P0.8mm",
        "LQFP48": "Package_QFP:LQFP-48_7x7mm_P0.5mm",
        "LQFP64": "Package_QFP:LQFP-64_10x10mm_P0.5mm",
        "LQFP100": "Package_QFP:LQFP-100_14x14mm_P0.5mm",
        "LQFP144": "Package_QFP:LQFP-144_20x20mm_P0.5mm",
        "LQFP176": "Package_QFP:LQFP-176_24x24mm_P0.5mm",
        "LQFP208": "Package_QFP:LQFP-208_28x28mm_P0.5mm",
        "TFBGA64": "Package_BGA:TFBGA-64_5x5mm_Layout8x8_P0.5mm",
        "TFBGA100": "Package_BGA:TFBGA-100_8x8mm_Layout10x10_P0.8mm",
        "TFBGA216": "Package_BGA:TFBGA-216_13x13mm_Layout15x15_P0.8mm",
        "TFBGA240": "Package_BGA:TFBGA-265_14x14mm_Layout17x17_P0.8mm",
        "TSSOP14": "Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
        "TSSOP20": "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
        "UFBGA64": "Package_BGA:UFBGA-64_5x5mm_Layout8x8_P0.5mm",
        "UFBGA100": "Package_BGA:UFBGA-100_7x7mm_Layout12x12_P0.5mm",
        "UFBGA132": "Package_BGA:UFBGA-132_7x7mm_Layout12x12_P0.5mm",
        # ST uses the name "UFBGA144" for two sizes of BGA, and there's no way
        # I can tell to pick them apart besides chip names
        "UFBGA144-7X7": "Package_BGA:UFBGA-144_7x7mm_Layout12x12_P0.5mm",
        "UFBGA144-10X10": "Package_BGA:UFBGA-144_10x10mm_Layout12x12_P0.8mm",
        "UFBGA169": "Package_BGA:UFBGA-169_7x7mm_Layout13x13_P0.5mm",
        "UFBGA176": "Package_BGA:UFBGA-201_10x10mm_Layout15x15_P0.65mm",
        "UFQFPN20": "Package_DFN_QFN:ST_UFQFPN-20_3x3mm_P0.5mm",
        "UFQFPN28": "Package_DFN_QFN:QFN-28_4x4mm_P0.5mm",
        "UFQFPN32": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        "UFQFPN48": "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm",
        "VFQFPN36": "Package_DFN_QFN:QFN-36-1EP_6x6mm_P0.5mm_EP4.1x4.1mm",
        "WLCSP25-DIE425": "Package_CSP:ST_WLCSP-25_Die425",
        "WLCSP25-DIE444": "Package_CSP:ST_WLCSP-25_Die444",
        "WLCSP25-DIE457": "Package_CSP:ST_WLCSP-25_Die457",
        "WLCSP36-DIE417": "Package_CSP:ST_WLCSP-36_Die417",
        "WLCSP36-DIE440": "Package_CSP:ST_WLCSP-36_Die440",
        "WLCSP36-DIE445": "Package_CSP:ST_WLCSP-36_Die445",
        "WLCSP36-DIE458": "Package_CSP:ST_WLCSP-36_Die458",
        "WLCSP49-DIE423": "Package_CSP:ST_WLCSP-49_Die423",
        "WLCSP49-DIE431": "Package_CSP:ST_WLCSP-49_Die431",
        "WLCSP49-DIE433": "Package_CSP:ST_WLCSP-49_Die433",
        "WLCSP49-DIE435": "Package_CSP:ST_WLCSP-49_Die435",
        "WLCSP49-DIE438": "Package_CSP:ST_WLCSP-49_Die438",
        "WLCSP49-DIE439": "Package_CSP:ST_WLCSP-49_Die439",
        "WLCSP49-DIE447": "Package_CSP:ST_WLCSP-49_Die447",
        "WLCSP49-DIE448": "Package_CSP:ST_WLCSP-49_Die448",
        "WLCSP63-DIE427": "Package_CSP:ST_WLCSP-63_Die427",
        "WLCSP64-DIE414": "Package_CSP:ST_WLCSP-64_Die414",
        "WLCSP64-DIE427": "Package_CSP:ST_WLCSP-64_Die427",
        "WLCSP64-DIE435": "Package_CSP:ST_WLCSP-64_Die435",
        "WLCSP64-DIE436": "Package_CSP:ST_WLCSP-64_Die436",
        "WLCSP64-DIE441": "Package_CSP:ST_WLCSP-64_Die441",
        "WLCSP64-DIE442": "Package_CSP:ST_WLCSP-64_Die442",
        "WLCSP64-DIE462": "Package_CSP:ST_WLCSP-64_Die462",
        "WLCSP66-DIE411": "Package_CSP:ST_WLCSP-66_Die411",
        "WLCSP66-DIE432": "Package_CSP:ST_WLCSP-66_Die432",
        "WLCSP72-DIE415": "Package_CSP:ST_WLCSP-72_Die415",
        "WLCSP81-DIE415": "Package_CSP:ST_WLCSP-81_Die415",
        "WLCSP81-DIE421": "Package_CSP:ST_WLCSP-81_Die421",
        "WLCSP81-DIE463": "Package_CSP:ST_WLCSP-81_Die463",
        "WLCSP90-DIE413": "Package_CSP:ST_WLCSP-90_Die413",
        "WLCSP100-DIE422": "Package_CSP:ST_WLCSP-100_Die422",
        "WLCSP100-DIE446": "Package_CSP:ST_WLCSP-100_Die446",
        "WLCSP100-DIE452": "Package_CSP:ST_WLCSP-100_Die452",
        "WLCSP100-DIE461": "Package_CSP:ST_WLCSP-100_Die461",
        "WLCSP104-DIE437": "Package_CSP:ST_WLCSP-104_Die437",
        "WLCSP143-DIE419": "Package_CSP:ST_WLCSP-143_Die419",
        "WLCSP143-DIE449": "Package_CSP:ST_WLCSP-143_Die449",
        "WLCSP144-DIE470": "Package_CSP:ST_WLCSP-144_Die470",
        "WLCSP168-DIE434": "Package_CSP:ST_WLCSP-168_Die434",
        "WLCSP180-DIE451": "Package_CSP:ST_WLCSP-180_Die451"
    }
    _FPFILTER_MAPPING = {
        "EWLCSP49-DIE447": "ST_WLCSP*Die447*",
        "EWLCSP66-DIE411": "ST_WLCSP*Die411*",
        "LFBGA100": "LFBGA*10x10mm*Layout10x10*P0.8mm*",
        "LFBGA144": "LFBGA*10x10mm*Layout12x12*P0.8mm*",
        "LQFP32": "LQFP*7x7mm*P0.8mm*",
        "LQFP48": "LQFP*7x7mm*P0.5mm*",
        "LQFP64": "LQFP*10x10mm*P0.5mm*",
        "LQFP100": "LQFP*14x14mm*P0.5mm*",
        "LQFP144": "LQFP*20x20mm*P0.5mm*",
        "LQFP176": "LQFP*24x24mm*P0.5mm*",
        "LQFP208": "LQFP*28x28mm*P0.5mm*",
        "TFBGA64": "TFBGA*5x5mm*Layout8x8*P0.5mm*",
        "TFBGA100": "TFBGA*8x8mm*Layout10x10*P0.8mm*",
        "TFBGA216": "TFBGA*13x13mm*Layout15x15*P0.8mm*",
        "TFBGA240": "TFBGA*14x14mm*Layout17x17*P0.8mm*",
        "TSSOP14": "TSSOP*4.4x5mm*P0.65mm*",
        "TSSOP20": "TSSOP*4.4x6.5mm*P0.65mm*",
        "UFBGA64": "UFBGA*5x5mm*Layout8x8*P0.5mm*",
        "UFBGA100": "UFBGA*7x7mm*Layout12x12*P0.5mm*",
        "UFBGA132": "UFBGA*7x7mm*Layout12x12*P0.5mm*",
        "UFBGA144-7X7": "UFBGA*7x7mm*Layout12x12*P0.5mm*",
        "UFBGA144-10X10": "UFBGA*10x10mm*Layout12x12*P0.8mm*",
        "UFBGA169": "UFBGA*7x7mm*Layout13x13*P0.5mm*",
        "UFBGA176": "UFBGA*10x10mm*Layout15x15*P0.65mm*",
        "UFQFPN20": "ST*UFQFPN*3x3mm*P0.5mm*",
        "UFQFPN28": "QFN*4x4mm*P0.5mm*",
        "UFQFPN32": "QFN*1EP*5x5mm*P0.5mm*",
        "UFQFPN48": "QFN*1EP*7x7mm*P0.5mm*",
        "VFQFPN36": "QFN*1EP*6x6mm*P0.5mm*",
        "WLCSP25-DIE425": "ST_WLCSP*Die425*",
        "WLCSP25-DIE444": "ST_WLCSP*Die444*",
        "WLCSP25-DIE457": "ST_WLCSP*Die457*",
        "WLCSP36-DIE417": "ST_WLCSP*Die417*",
        "WLCSP36-DIE440": "ST_WLCSP*Die440*",
        "WLCSP36-DIE445": "ST_WLCSP*Die445*",
        "WLCSP36-DIE458": "ST_WLCSP*Die458*",
        "WLCSP49-DIE423": "ST_WLCSP*Die423*",
        "WLCSP49-DIE431": "ST_WLCSP*Die431*",
        "WLCSP49-DIE433": "ST_WLCSP*Die433*",
        "WLCSP49-DIE435": "ST_WLCSP*Die435*",
        "WLCSP49-DIE438": "ST_WLCSP*Die438*",
        "WLCSP49-DIE439": "ST_WLCSP*Die439*",
        "WLCSP49-DIE447": "ST_WLCSP*Die447*",
        "WLCSP49-DIE448": "ST_WLCSP*Die448*",
        "WLCSP63-DIE427": "ST_WLCSP*Die427*",
        "WLCSP64-DIE414": "ST_WLCSP*Die414*",
        "WLCSP64-DIE427": "ST_WLCSP*Die427*",
        "WLCSP64-DIE435": "ST_WLCSP*Die435*",
        "WLCSP64-DIE436": "ST_WLCSP*Die436*",
        "WLCSP64-DIE441": "ST_WLCSP*Die441*",
        "WLCSP64-DIE442": "ST_WLCSP*Die442*",
        "WLCSP64-DIE462": "ST_WLCSP*Die462*",
        "WLCSP66-DIE411": "ST_WLCSP*Die411*",
        "WLCSP66-DIE432": "ST_WLCSP*Die432*",
        "WLCSP72-DIE415": "ST_WLCSP*Die415*",
        "WLCSP81-DIE415": "ST_WLCSP*Die415*",
        "WLCSP81-DIE421": "ST_WLCSP*Die421*",
        "WLCSP81-DIE463": "ST_WLCSP*Die463*",
        "WLCSP90-DIE413": "ST_WLCSP*Die413*",
        "WLCSP100-DIE422": "ST_WLCSP*Die422*",
        "WLCSP100-DIE446": "ST_WLCSP*Die446*",
        "WLCSP100-DIE452": "ST_WLCSP*Die452*",
        "WLCSP100-DIE461": "ST_WLCSP*Die461*",
        "WLCSP104-DIE437": "ST_WLCSP*Die437*",
        "WLCSP143-DIE419": "ST_WLCSP*Die419*",
        "WLCSP143-DIE449": "ST_WLCSP*Die449*",
        "WLCSP144-DIE470": "ST_WLCSP*Die470*",
        "WLCSP168-DIE434": "ST_WLCSP*Die434*",
        "WLCSP180-DIE451": "ST_WLCSP*Die451*"
    }

    pdfinfo = {}

    def __init__(self, xmlfile, pdfdir):
        logging.debug(xmlfile)
        self.xmlfile = xmlfile
        self.pdfdir = pdfdir
        self.name = ""
        self.package = ""
        self.footprint = ""
        self.pins = []
        self.aliases = []

        self.read_info()

    def read_info(self):
        self.tree = etree.parse(self.xmlfile)
        self.root = self.tree.getroot()

        self.ns = {"a": self.root.nsmap[None]}  # I hate XML

        name = self.root.get("RefName")

        # Get all the part names for this part
        als = Device._name_search.search(name)
        if als:
            pre = als.group(1)
            post = als.group(3)
            s = als.group(2).split("-")
            self.name = pre + s[0] + post
            for a in s[1:]:
                self.aliases.append(pre + a + post)
        else:
            self.name = name

        # Get the package code
        self.package = self.root.get("Package")
        # Differentiate the WLCSP packages by die code
        if "WLCSP" in self.package:
            die = self.root.xpath("a:Die", namespaces=self.ns)[0].text
            self.package += f"-{die}"
        # Pick the right size of UFBGA144
        if self.package == "UFBGA144":
            if self.name in {"STM32F412ZEJx", "STM32F413ZGJx", "STM32F423ZHJx",
                    "STM32F446ZCJx", "STM32L4R9ZGJx", "STM32L4S9ZIJx"}:
                self.package += "-10X10"
            elif self.name in {"STM32F446ZCHx", "STM32F723ZCIx",
                    "STM32F733ZEIx"}:
                self.package += "-7X7"
            else:
                logging.warning(f"Unable to determine package variant for "
                        f"device {self.name}, package {self.package}")

        # Get the footprint for this package
        try:
            self.footprint = Device._FOOTPRINT_MAPPING[self.package]
        except KeyError:
            logging.warning(f"No footprint found for device {self.name}, "
                    f"package {self.package}")
            self.footprint = ""

        # Read the information for each pin
        for child in self.root.xpath("a:Pin", namespaces=self.ns):
            # Create object and read attributes
            newpin = DataPin(child.get("Position"), child.get("Name"), child.get("Type"))

            if newpin.name in Device._SPECIAL_PIN_MAPPING:
                newpin.name = Device._SPECIAL_PIN_MAPPING[newpin.name][0]
            else:
                newpin.name = Device._pinname_split.split(newpin.name)[0]

            # Fix type for NC pins
            if newpin.name == "NC":
                newpin.pintype = "NC"

            # Get alternate functions
            for signal in child.xpath("a:Signal", namespaces=self.ns):
                altfunction = signal.get("Name")
                # If the pin doesn't have a name, use the first alt function
                if not newpin.name:
                    newpin.name = altfunction
                # If an alt function corresponds to a pin type, set that
                if altfunction in Device._SPECIAL_TYPES_MAPPING:
                    newpin.pintype = Device._SPECIAL_TYPES_MAPPING[altfunction]

            self.pins.append(newpin)

        # If this part has a power pad, we have to add it manually
        if (self.root.get("HasPowerPad") == "true"
                or self.package in Device._POWER_PAD_FIX_PACKAGES):
            # Read pin count from package name
            packPinCountR = Device._pincount_search.search(self.package)
            powerpinnumber = str(int(packPinCountR.group(1)) + 1)
            logging.info(f"Device {name} with powerpad, package {self.package}, power pin: {powerpinnumber}")
            # Create power pad pin
            powerpadpin = DataPin(powerpinnumber, "VSS", "Power")
            self.pins.append(powerpadpin)

        # Parse information for documentation
        self.core = self.root.xpath("a:Core", namespaces=self.ns)[0].text
        self.family = self.root.get("Family")
        self.line = self.root.get("Line")
        try:
            self.freq = self.root.xpath("a:Frequency", namespaces=self.ns)[0].text
        except:
            # Not all chips have a frequency specification
            logging.info("Unknown frequency")
            self.freq = None
        self.ram = [r.text for r in self.root.xpath("a:Ram", namespaces=self.ns)]
        self.io = self.root.xpath("a:IONb", namespaces=self.ns)[0].text
        self.flash = [f.text for f in self.root.xpath("a:Flash", namespaces=self.ns)]
        try:
            self.voltage = [self.root.xpath("a:Voltage", namespaces=self.ns)[0].get("Min", default="--"), self.root.xpath("a:Voltage", namespaces=self.ns)[0].get("Max", default="--")]
        except:
            # Not all chips have a voltage specification
            logging.info("Unknown voltage")
            self.voltage = None

        # Get the datasheet filename
        self.pdf = self.readpdf()

        # Merge any duplicated pins
        self.merge_duplicate_pins()

    def create_symbol(self, gen):
        # Make strings for DCM entries
        freqstr = f"{self.freq}MHz, " if self.freq else ""
        voltstr = f"{self.voltage[0]}-{self.voltage[1]}V, " if self.voltage else ""
        pkgstr = self._pkgname_sub.sub(r'\1-\2', self.package)
        desc_fmt = (f"{self.core} MCU, {{flash}}KB flash, "
                f"{{ram}}KB RAM, {freqstr}{voltstr}{self.io} GPIO, "
                f"{pkgstr}")
        keywords = f"{self.core} {self.family} {self.line}"
        datasheet = "" if self.pdf is None else (f"http://www.st.com/"
                f"st-web-ui/static/active/en/resource/technical/document/"
                f"datasheet/{self.pdf}")

        # Make the symbol
        self.symbol = gen.addSymbol(self.name, dcm_options={
                'description': desc_fmt.format(flash=self.flash[0],
                    ram=self.ram[0]),
                'keywords': keywords,
                'datasheet': datasheet},
                offset=20)

        # Add aliases
        for i, alias in enumerate(self.aliases):
            f = 0 if len(self.flash) == 1 else i+1
            r = 0 if len(self.ram) == 1 else i+1
            self.symbol.addAlias(alias, dcm_options={
                'description': desc_fmt.format(flash=self.flash[f],
                    ram=self.ram[r]), 'keywords': keywords, 'datasheet':
                datasheet})

        # Add footprint filters
        try:
            self.symbol.addFootprintFilter(Device._FPFILTER_MAPPING[self.package])
        except KeyError:
            logging.warning(f"No footprint filters found for device "
                    f"{self.name}, package {self.package}")

        # Draw the symbol
        self.draw_symbol()

    def xcompare(self, x, y):
        for a, b in zip(x, y):
            if a != b and a != 'x' and b != 'x':
                return False
        return True

    @classmethod
    def readpdfinfo(cls, pdfdir):
        for _, _, filenames in os.walk(pdfdir):
            files = [fn for fn in filenames if fn.endswith(".pdf.par")]
            break

        for pdf in files:
            p = open(os.path.join(pdfdir, pdf), "r")
            for line in p:
                line = line.strip()
                if line.find("STM32") >= 0:
                    # Remove commas and then split string
                    candidatenames = line.translate(str.maketrans(","," ")).split()
                    for candidatename in candidatenames:
                        # Associate file with every device name
                        cls.pdfinfo[candidatename] = pdf
                # Assume that the device names are always at the beginning of file
                if not line.startswith("STM32"):
                    break

    def readpdf(self):
        # Read device names from PDFs if we haven't yet
        if not Device.pdfinfo:
            Device.readpdfinfo(self.pdfdir)

        s = self.name
        #logging.debug("NEW: " + s)
        #logging.debug(Device.pdfinfo)
        winners = set()
        for key, value in Device.pdfinfo.items():
            # Some heuristic here
            minussplit = key.split("-")
            variants = minussplit[0].split("/")
            if len(minussplit) > 1:
                suffix = "x" + "x".join(minussplit[1:])
            else:
                suffix = ""
            strings = [suffix + variants[0]]
            for var in variants[1:]:
                strings.append(strings[0][:-len(var)] + var + suffix)
            for string in strings:
                if self.xcompare(s, string):
                    winners.add(value)

        #logging.debug(winners)
        if len(winners) == 1:
            return winners.pop()[:-4]
        else:
            if winners:
                logging.warning(f"Multiple datasheets determined for device "
                        f"{self.name} ({winners})")
            else:
                logging.warning(f"Datasheet could not be determined for "
                        f"device {self.name}")
            return None

    def merge_duplicate_pins(self):
        pinNumMap = {}
        removePins = []
        for pin in self.pins:
            if pin.num in pinNumMap:
                logging.info(f"Duplicated pin {pin.num} in part {self.name}, merging")
                mergedPin = pinNumMap[pin.num]
                mergedPin.name += f"/{pin.name}"
                removePins.append(pin)
            else:
                pinNumMap[pin.num] = pin

        for pin in removePins:
            self.pins.remove(pin)

    def draw_symbol(self):
        resetPins = []
        bootPins = []
        powerPins = []
        clockPins = []
        ncPins = []
        otherPins = []
        ports = {}

        leftPins = []
        rightPins = []
        topPins = []
        bottomPins = []

        # Get pin length
        # NOTE: there is a typo in the library making it so we have to call
        # this "pin_lenght" when making the drawing pin.  Whoops!
        pin_length = 100 if all(len(pin.num) < 3 for pin in self.pins) else 200

        # Classify pins
        for pin in self.pins:
            # I/O pins - uncertain orientation
            if ((pin.pintype == "I/O" or pin.pintype == "Clock")
                    and pin.name.startswith("P")):
                port = pin.name[1]
                pin_num = int(Device._number_findall.findall(pin.name)[0])
                try:
                    ports[port][pin_num] = pin.to_drawing_pin(
                            pin_length=pin_length)
                except KeyError:
                    ports[port] = {}
                    ports[port][pin_num] = pin.to_drawing_pin(
                            pin_length=pin_length)
            # Clock pins go on the left
            elif pin.pintype == "Clock":
                clockPins.append(pin.to_drawing_pin(pin_length=pin_length,
                        orientation=DrawingPin.PinOrientation.RIGHT))
            # Power pins
            elif pin.pintype == "Power" or pin.name.startswith("VREF"):
                # Positive pins go on the top
                if pin.name.startswith("VDD") or pin.name.startswith("VBAT"):
                    topPins.append(pin.to_drawing_pin(
                            pin_length=pin_length,
                            orientation=DrawingPin.PinOrientation.DOWN))
                # Negative pins go on the bottom
                elif pin.name.startswith("VSS"):
                    bottomPins.append(pin.to_drawing_pin(
                            pin_length=pin_length,
                            orientation=DrawingPin.PinOrientation.UP))
                # Other pins go on the left
                else:
                    powerPins.append(pin.to_drawing_pin(pin_length=pin_length,
                            orientation=DrawingPin.PinOrientation.RIGHT))
            # Reset pins go on the left
            elif pin.pintype == "Reset":
                resetPins.append(pin.to_drawing_pin(pin_length=pin_length,
                        orientation=DrawingPin.PinOrientation.RIGHT))
            # Boot pins go on the left
            elif pin.pintype == "Boot":
                bootPins.append(pin.to_drawing_pin(pin_length=pin_length,
                        orientation=DrawingPin.PinOrientation.RIGHT))
            # NC pins go in their own group
            elif pin.pintype == "NC":
                ncPins.append(pin.to_drawing_pin(pin_length=pin_length,
                        orientation=DrawingPin.PinOrientation.RIGHT))
            # Other pins go on the left
            else:
                otherPins.append(pin.to_drawing_pin(pin_length=pin_length,
                        orientation=DrawingPin.PinOrientation.RIGHT))

        # Apply pins to sides
        leftGroups = []
        rightGroups = []

        leftSpace = 0
        rightSpace = 0

        # Special groups go to the left
        if len(resetPins) > 0:
            leftGroups.append(resetPins)
        if len(bootPins) > 0:
            leftGroups.append(bootPins)
        if len(powerPins) > 0:
            leftGroups.append(sorted(powerPins, key=lambda p: p.name))
        if len(clockPins) > 0:
            leftGroups.append(clockPins)
        if len(otherPins) > 0:
            leftGroups.append(otherPins)

        # Count the space needed for special groups
        for group in leftGroups:
            leftSpace += len(group) + 1

        serviceSpace = leftSpace

        # Add ports to the right, counting the space needed
        for _, port in sorted(ports.items()):
            pins = [pin for _, pin in sorted(port.items())]
            rightSpace += len(pins) + 1
            rightGroups.append(pins)

        # Move ports to the left from the right until moving one more would
        # make the symbol get taller.
        maxSize = max(leftSpace, rightSpace)
        movedSpace = 0
        movedGroups = []
        while True:
            groupToMove = rightGroups[-1]
            newLeftSpace = leftSpace + len(groupToMove) + 1
            newRightSpace = rightSpace - len(groupToMove) - 1
            newSize = max(newLeftSpace, newRightSpace)
            if newSize >= maxSize:
                break
            maxSize = newSize
            leftSpace = newLeftSpace
            rightSpace = newRightSpace

            movedSpace += len(groupToMove) + 1

            movedGroups.append(groupToMove)
            rightGroups.pop()

        # Calculate height of the symbol
        box_height = max(leftSpace, rightSpace) * 100

        # Calculate the width of the symbol
        round_up = lambda x, y: (x + y - 1) // y * y
        pin_name_width = lambda p: len(p.name) * 47
        pin_group_max_width = lambda g: max(map(pin_name_width, g))
        left_width = round_up(max(map(pin_group_max_width,
                leftGroups + movedGroups)), 100)
        right_width = round_up(max(map(pin_group_max_width, rightGroups)), 100)
        top_width = len(topPins) * 100
        bottom_width = len(bottomPins) * 100
        middle_width = 100 + max(top_width, bottom_width)
        box_width = left_width + middle_width + right_width

        # Add the body rectangle
        self.symbol.drawing.append(DrawingRectangle(Point(0, 0),
                Point(box_width, box_height), unit_idx=0,
                fill=ElementFill.FILL_BACKGROUND))

        # Add the moved pins (bottom left)
        y = 100
        for group in reversed(movedGroups):
            for pin in reversed(group):
                pin.at = Point(-pin_length, y)
                pin.orientation = DrawingPin.PinOrientation.RIGHT
                self.symbol.drawing.append(pin)
                y += 100
            y += 100

        # Add the left pins (top left)
        y = box_height - 100
        for group in leftGroups:
            for pin in group:
                pin.at = Point(-pin_length, y)
                pin.orientation = DrawingPin.PinOrientation.RIGHT
                self.symbol.drawing.append(pin)
                y -= 100
            y -= 100

        # Add the right pins
        y = 100
        for group in reversed(rightGroups):
            for pin in reversed(group):
                pin.at = Point(box_width + pin_length, y)
                pin.orientation = DrawingPin.PinOrientation.LEFT
                self.symbol.drawing.append(pin)
                y += 100
            y += 100

        # Add the top pins
        x = (left_width + (100 + middle_width) // 2 - top_width // 2) // 100 * 100
        for pin in sorted(topPins, key=lambda p: p.name):
            pin.at = Point(x, box_height + pin_length)
            pin.orientation = DrawingPin.PinOrientation.DOWN
            self.symbol.drawing.append(pin)
            x += 100
        last_top_x = x

        # Add the bottom pins
        x = (left_width + (100 + middle_width) // 2 - bottom_width // 2) // 100 * 100
        for pin in sorted(bottomPins, key=lambda p: p.name):
            pin.at = Point(x, -pin_length)
            pin.orientation = DrawingPin.PinOrientation.UP
            self.symbol.drawing.append(pin)
            x += 100

        # Add the NC pins
        y = 100
        for pin in ncPins:
            pin.at = Point(0, y)
            pin.orientation = DrawingPin.PinOrientation.RIGHT
            self.symbol.drawing.append(pin)
            y += 100
        y += 100

        # Center the symbol
        translate_center = Point(-box_width//2//100*100,
                -box_height//2//100*100)
        self.symbol.drawing.translate(translate_center)

        # when creating the string, vertical and horizontal alignment get
        # switched, so we switch them here to make the result correct
        self.symbol.setReference('U',
                at=Point(0, box_height + 50).translate(translate_center),
                alignment_vertical=SymbolField.FieldAlignment.LEFT)
        self.symbol.setValue(value=self.name,
                at=Point(last_top_x,
                box_height + 50).translate(translate_center),
                alignment_vertical=SymbolField.FieldAlignment.LEFT)
        self.symbol.setDefaultFootprint(value=self.footprint,
                at=translate_center,
                alignment_vertical=SymbolField.FieldAlignment.RIGHT,
                visibility=SymbolField.FieldVisibility.INVISIBLE)


def main():
    parser = argparse.ArgumentParser(
            description='Generator for STM32 microcontroller symbols')
    parser.add_argument('xmldir',
            help='Directory containing ONLY valid STM32 XML files')
    parser.add_argument('pdfdir',
            help='Directory containing STM32 datasheet PDFs')
    parser.add_argument('-v', '--verbose', action='count', default=0,
            help='Print more information')

    args = parser.parse_args()

    if not os.path.isdir(args.xmldir) or not os.path.isdir(args.pdfdir):
        parser.error("xmldir and pdfdir must be directories")

    if args.verbose == 0:
        loglevel = logging.WARNING
    elif args.verbose == 1:
        loglevel = logging.INFO
    elif args.verbose >= 2:
        loglevel = logging.DEBUG

    logging.basicConfig(format='%(levelname)s:%(message)s', level=loglevel)

    # Parse text from PDFs
    for _, _, filenames in os.walk(args.pdfdir):
        for pdffile in filenames:
            pdffile = os.path.join(args.pdfdir, pdffile)
            pdfparsedfile = pdffile + ".par"
            if not os.path.isfile(pdfparsedfile) and pdffile.endswith(".pdf"):
                logging.info(f"Converting: {pdffile}")
                os.system("pdf2txt.py -o " + pdfparsedfile + " " + pdffile)
        break

    # Load devices from XML, sorted by family
    libraries = {}
    for _, _, filenames in os.walk(args.xmldir):
        filenames.sort()
        for xmlfile in filenames:
            # Load information about the part(s)
            mcu = Device(os.path.join(args.xmldir, xmlfile), args.pdfdir)
            # If there isn't a SymbolGenerator for this family yet, make one
            if mcu.family not in libraries:
                libraries[mcu.family] = SymbolGenerator(
                        lib_name=f"MCU_ST_{mcu.family}")
            # If the part has a datasheet PDF, make a symbol for it
            if mcu.pdf is not None:
                mcu.create_symbol(libraries[mcu.family])
        break

    # Write libraries
    for gen in libraries.values():
        gen.writeFiles()

if __name__ == "__main__":
    main()
