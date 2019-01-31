# -*- coding: utf-8 -*-

from rules.rule import *


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rules for pin stacking')
        self.different_names = False
        self.NC_stacked = False
        self.different_types = False
        self.only_one_visible = False
        # variables for fixing special pin-stack pins
        self.fix_make_invisible = set()
        self.fix_make_visible = set()
        self.fix_make_passive = set()

    def stackStr(self, stack):
        multi_unit = int(self.component.definition['unit_count']) > 1
        unit_str = " (unit {u})".format(u=stack['u']) if multi_unit else ""

        # WHY are pins flipped vertically? Mega sad face :(
        return "Pinstack @ ({x},{y}){u}".format(
            x=int(stack['x']),
            y=-1 * int(stack['y']),
            u=unit_str)

    def pinStr(self, pin):
        multi_unit = int(self.component.definition['unit_count']) > 1

        if multi_unit:
            unit = pin['unit']
        else:
            unit = None

        return pinString(pin, unit)

    def check(self):
        self.component.padInSpecialPowerStack = set()

        # List of lists of pins that are entirely duplicated
        self.duplicated_pins = []

        pin_locations = []

        for pin in self.component.pins:

            # To be "identical", all following properties much be the same

            pinx = pin['posx']     # x coordinate
            piny = pin['posy']     # y coordinate
            pinu = pin['unit']     # unit (for multi-unit parts)
            pinc = pin['convert']  # convert (de morgan)

            dupe = False

            for loc in pin_locations:

                locx = loc['x']
                locy = loc['y']
                locu = loc['u']
                locc = loc['c']

                if pinx == locx and piny == locy and pinu == locu and pinc == locc:
                    loc['pins'].append(pin)
                    dupe = True

            if not dupe:
                new_loc = {'x': pinx, 'y': piny, 'u': pinu, 'c': pinc}
                new_loc['pins'] = [pin]
                pin_locations.append(new_loc)

        err = False

        for loc in pin_locations:
            if len(loc['pins']) > 1:

                pin_units = set()
                pin_nums = set()
                pin_names = set()
                pin_etypes = set()

                vis_pin_count = 0

                for pin in loc['pins']:
                    pin_nums.add(pin['num'])
                    pin_names.add(pin['name'])
                    pin_units.add(pin['unit'])
                    pin_etypes.add(pin['electrical_type'])

                    # Add visibile pins
                    if not pin['pin_type'].startswith('N'):
                        vis_pin_count += 1

                    # NC pins must never be stacked
                    if pin['electrical_type'] == 'N':
                        self.error("NC {pin} @ ({x},{y})is stacked on other pins".format(
                            pin=self.pinStr(pin),
                            x=pin['posx'],
                            y=-1*int(pin['posy'])))
                        err = True
                        self.NC_stacked = True

                # Fewer pin numbers than pins
                if len(pin_nums) < len(loc['pins']):
                    self.error("Duplicate pins @ ({x},{y})".format(
                        x=loc['x'],
                        y=-1 * int(loc['y'])))
                    err = True
                    for pin in loc['pins']:
                        self.errorExtra(self.pinStr(pin))

                    # If ALL pins are identical, go to next group (no further checks needed)
                    if len(pin_nums) == len(pin_names) == len(pin_units) == 1:
                        self.duplicated_pins.append([pin for pin in loc['pins']])
                        continue

                # Different names!
                if len(pin_names) > 1:
                    self.error(self.stackStr(loc) + " have different names")
                    err = True
                    for pin in loc['pins']:
                        self.errorExtra(self.pinStr(pin))
                        self.different_names = True

                # Different types!
                isSpecialXPassivePinStack = False
                isSpecialSingleTypeStack = ((len(pin_etypes) == 1) and (("w" in pin_etypes) or ("O" in pin_etypes)))
                if (len(pin_etypes) > 1) or isSpecialSingleTypeStack:
                    # an exception is done for some special pin-stacks:
                    # isSpecialXPassivePinStack are those pins stacks that fulfill one of the following conditions:
                    #    1. consists only of output and passive pins
                    #    2. consists only of power-output and passive pins
                    #    3. consists only of power-input and passive pins
                    #    4. consists only of power-output/output pins (isSpecialSingleTypeStack)
                    if ((len(pin_etypes) == 2) and ("O" in pin_etypes) and ("P" in pin_etypes)) or ((len(pin_etypes) == 2) and ("w" in pin_etypes) and ("P" in pin_etypes)) or ((len(pin_etypes) == 2) and ("W" in pin_etypes) and ("P" in pin_etypes)) or isSpecialSingleTypeStack:
                        isSpecialXPassivePinStack = True

                    # a non-special pin-stack needs to have all pins of the same type
                    if not isSpecialXPassivePinStack:
                        self.error(self.stackStr(loc) + " have different types")
                        err = True
                        for pin in loc['pins']:
                            self.errorExtra("{pin} : {etype}".format(
                                pin=self.pinStr(pin),
                                etype=pinElectricalTypeToStr(pin['electrical_type'])))
                            self.different_types = True
                    else:
                        # in special pin stacks the power-input/power-output/output pin has to be visible and the passive pins need to be invisible
                        specialpincount = 0
                        for pin in loc['pins']:
                            self.component.padInSpecialPowerStack.add(pin['num'])
                            # check if all passive pins are invisible
                            if pin['electrical_type'] == 'P' and (not pin['pin_type'].startswith('N')):
                                self.errorExtra("{pin} : {etype} should be invisible (power-pin stack)".format(
                                    pin=self.pinStr(pin),
                                    etype=pinElectricalTypeToStr(pin['electrical_type'])))
                                err = True
                                self.fix_make_invisible.add(pin['num'])
                            # check if power-pin is visible
                            if (pin['electrical_type'] == 'O' or pin['electrical_type'] == 'w' or pin['electrical_type'] == 'W'):
                                if pin['pin_type'].startswith('N'):
                                    self.errorExtra("{pin} : {etype} should be visible in a power-in/power-out/output pin stack".format(
                                        pin=self.pinStr(pin),
                                        etype=pinElectricalTypeToStr(pin['electrical_type'])))
                                    err = True
                                    self.fix_make_visible.add(pin['num'])
                                    specialpincount += 1
                                    if specialpincount <= 1:
                                        self.fix_make_visible.add(pin['num'])
                                else:
                                    specialpincount += 1
                            if specialpincount > 1:
                                self.errorExtra("{pin} : {etype} should be an invisible PASSIVE pin power-in/power-out/output pin stack".format(
                                    pin=self.pinStr(pin),
                                    etype=pinElectricalTypeToStr(pin['electrical_type'])))
                                self.fix_make_invisible.add(pin['num'])
                                self.fix_make_passive.add(pin['num'])

                # Only one pin should be visible (checks have already been done, when isSpecialXPassivePinStack=true)
                if (not isSpecialXPassivePinStack) and (not vis_pin_count == 1):
                    self.error(self.stackStr(loc) + " must have exactly one (1) visible pin")
                    err = True
                    for pin in loc['pins']:
                        self.errorExtra("{pin} is {vis}".format(
                            pin=self.pinStr(pin),
                            vis='INVISIBLE' if pin['pin_type'].startswith('N') else 'VISIBLE'))
                        self.only_one_visible = True

        # check for invisible power I/O-pins (unless in power.lib)
        isPowerLib = (self.component.reference == '#PWR')
        if (not err) and (not isPowerLib):
            for pin in self.component.pins:
                if ((pin['electrical_type'] == 'w') or (pin['electrical_type'] == 'W')) and pin['pin_type'].startswith('N'):
                    self.errorExtra("{pin} : {etype} should be visible (power-in/power-out pins may never be invisible, unless in a power-net tag/symbol)".format(
                                    pin=self.pinStr(pin),
                                    etype=pinElectricalTypeToStr(pin['electrical_type'])))
                    self.fix_make_visible.add(pin['num'])
                    err = True
        return err

    def fix(self):
        # Delete duplicate pins
        if len(self.duplicated_pins) > 0:
            self.info("Removing duplicate pins")

            for pin_groups in self.duplicated_pins:
                # Leave first pin and delete all others
                pin = pin_groups[0]

                count = 0
                # Iterate through component pins
                i = 0
                while i < len(self.component.drawOrdered):

                    el = self.component.drawOrdered[i]
                    if not el[0] == 'X':  # Pins
                        i += 1
                        continue

                    p_test = el[1]

                    # All these keys must be identical!
                    keys = ['name', 'num', 'unit', 'posx', 'posy', 'convert']

                    # Found duplicate
                    if all([p_test[key] == pin[key] for key in keys]):
                        count += 1
                        # Skip the first instance, delete all others
                        if count > 1:
                            del self.component.drawOrdered[i]
                            self.info("Deleting {pin} @ ({x},{y})".format(
                                pin=self.pinStr(pin),
                                x=pin['posx'],
                                y=pin['posy']))
                            continue
                    i += 1

        for pin in self.component.pins:
            if pin['num'] in self.fix_make_passive:
                pin['electrical_type'] = 'P'
                self.info("pin "+pin['num']+" "+pin['name']+" is passive now (pin['electrical_type']="+pin['electrical_type']+")")
            if pin['num'] in self.fix_make_invisible:
                pin['pin_type'] = 'N'+pin['pin_type']
                self.info("pin "+pin['num']+" "+pin['name']+" is invisible now (pin['pin_type']="+pin['pin_type']+")")
            if pin['num'] in self.fix_make_visible:
                pin['pin_type'] = pin['pin_type'][1:len(pin['pin_type'])]
                self.info("pin "+pin['num']+" "+pin['name']+" is visible now (pin['pin_type']="+pin['pin_type']+")")

        if self.different_names:
            self.info("FIX for 'different pin names' not supported (yet)! Please fix manually.")
        if self.NC_stacked:
            self.info("FIX for 'NC pins stacked' not supported! Please fix manually.")
        if self.different_types:
            self.info("FIX for 'different pin types' not supported (yet)! Please fix manually.")
        if self.only_one_visible:
            self.info("FIX for 'only one pin in a pin stack is visible' not supported (yet)! Please fix manually.")
