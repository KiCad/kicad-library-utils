# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Rule 3.1', 'Using a 100mils grid, pin ends and origin must lie on grid nodes (IEC-60617).')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * violating_pins
        """
        self.violating_pins = []
        for pin in self.component.pins:
            posx = int(pin['posx'])
            posy = int(pin['posy'])
            if (posx % 100) != 0 or (posy % 100) != 0:
                self.violating_pins.append(pin)
                self.verboseOut(Verbosity.HIGH, Severity.ERROR, 'pin: %s (%s), posx %s, posy %s' %
                           (pin['name'], pin['num'], pin['posx'], pin['posy']))

        return True if len(self.violating_pins) > 0 else False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.verboseOut(Verbosity.NORMAL, Severity.INFO, "FIX: not yet supported" )
        # TODO
