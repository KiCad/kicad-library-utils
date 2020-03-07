# -*- coding: utf-8 -*-
#
# Description:
#       For THT parts, following layers required:
#       *.Cu
#       F.Mask
#       B.Mask
#
#       These rules do not apply for thermal_vias in exposed pad.
#       This is a second check, to see whether it is a thermal via or not.
#       If it is, only *.Cu is required
#
#

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Pad requirements for THT footprints')

        self.required_layers = ["*.Cu","*.Mask"]



    def checkPads(self, pads):

        self.wrong_layers = []

        errors = []

        padNoMax = 0

        EParray = [] # Array of exposed pad properties: x, y, x-width, y-width

        module = self.module
        fpName = module.name

        # Check if footprint name contains the standard text strings for
        # footprints with exposed pad
        # Looks for the string:
        # '-xEP' where x is any number between 0 and 9 and designates number of exposed pads.
        # EP is NOT case sensitive and registers 'ep' just as well as 'EP'
        exposed_pad_search = re.search('\-\d+[EP]{2}', fpName, re.IGNORECASE)

        if exposed_pad_search:
            noExposedPads = int(re.findall('\d', exposed_pad_search.group(0))[0])

            # Finds the maximum pad number
            for pad in pads:
                if pad['type'] == 'smd' and 'F.Cu' in pad['layers']:
                    #print(pad['number'], pad['layers'])
                    try:
                        if pad['number'] > padNoMax:
                            padNoMax = pad['number']
                    except:
                        break

            # Gets the (x,y) coordinates and x-width and y-width for the exposed pads
            for num in range(noExposedPads):
                for pad in pads:
                    if pad['type'] == 'smd' and 'F.Cu' in pad['layers']:
                        if pad['number'] == (padNoMax - num):
                            p_x, p_y = pad['pos']['x'], pad['pos']['y'] #center pad coordinates
                            pad_size = pad['size']
                            size_x, size_y = pad_size['x'], pad_size['y'] # x-width and y-width
                            EParray.append([p_x, p_y, size_x, size_y])

            # print("Exposed pad array: ", EParray) # Debug

        # testvar = 0 # debug
        for pad in pads:
            layers = pad['layers']

            # Skip if SMD pad
            if not pad['type'] == 'thru_hole':
                continue

            skip = False

            # If the array of exposed pads is not empty
            if EParray:
                # Check to see if the via's origin (x,y) is contained within a square
                # around the exposed pad with origin (EP_x, EP_y) and
                # width EP_size_x and length EP_size_y
                for EP in EParray:
                    p_x = pad['pos']['x'] # current pad
                    p_y = pad['pos']['y'] # current pad

                    EP_x = EP[0] # exposed pad x coordinate
                    EP_y = EP[1] # exposed pad y coordinate
                    EP_size_x = EP[2] # exposed pad x-width
                    EP_size_y = EP[3] # exposed pad y-width
                    if (EP_x + EP_size_x - p_x) > 0 and (EP_y + EP_size_y - p_y) > 0 and (EP_x - EP_size_x - p_x) < 0 and (EP_y - EP_size_y - p_y) < 0:
                        # print("Number: ", pad['number'], "Pad:", p_x, p_y, "Size:", pad['size']['x'], pad['size']['y'], "Layers:", pad['layers']) # debug
                        # testvar = testvar + 1 # debug
                        skip = True

            err = False

            # Check required layers
            for layer in self.required_layers:
                if layer not in layers and not skip:
                    errors.append("Pad '{n}' missing layer '{lyr}'".format(
                        n=pad['number'],
                        lyr=layer))
                    err = True

            # Check for extra layers
            for layer in layers:
                if layer not in self.required_layers:
                    errors.append("Pad '{n}' has extra layer '{lyr}'".format(
                        n = pad['number'],
                        lyr = layer))
                    err = True

            if err:
                self.wrong_layers.append(pad)

        # print(testvar) # Debug

        if len(errors) > 0:
            self.error("Some THT pads have incorrect layer settings")
            for msg in errors:
                self.errorExtra(msg)

        return len(self.wrong_layers) > 0

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * pin1_position
            * pin1_count
        """
        module = self.module

        return any([self.checkPads(module.pads)])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module

        for pad in module.filterPads('thru_hole'):
            self.info("Pad {n} - Setting required layers for THT pad".format(n=pad['number']))
            pad['layers'] = self.required_layers

