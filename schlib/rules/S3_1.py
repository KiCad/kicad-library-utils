# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Origin is be centered on the middle of the symbol')

    def check(self):

        """
        Calculate the 'bounds' of the symbol based on pin locations
        """

        x_min = y_min = x_max = y_max = None

        pins = self.component.pins

        # No pins? Ignore check.
        # This can be improved to include graphical items too...
        if len(pins) == 0:
            return False

        for i, p in enumerate(pins):

            x = int(p['posx'])
            y = int(p['posy'])

            if i == 0:
                x_min = x_max = x
                y_min = y_max = y
            else:
                x_min = min(x_min, x)
                x_max = max(x_max, x)
                y_min = min(y_min, y)
                y_max = max(y_max, y)

        # Center point average
        x = (x_min + x_max) / 2
        y = (y_min + y_max) / 2

        # Right on the middle!
        if x == 0 and y == 0:
            return False
        else:
            self.warning("Symbol not centered on origin")
            self.warningExtra("Center calculated @ ({x}, {y})".format(x=x, y=y))

        return False

    def fix(self):

        self.recheck()


