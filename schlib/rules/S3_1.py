# -*- coding: utf-8 -*-

from rules.rule import *
import math


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Origin is centered on the middle of the symbol')

    def check(self):
        """
        Calculate the 'bounds' of the symbol based on rectangle (if only a
        single filled rectangle is present) or on pin positions.
        """

        # If there is only a single filled rectangle, we assume that it is the
        # main symbol outline.
        drawing = self.component.draw
        filled_rects = [rect for rect in drawing['rectangles']
                        if rect['fill'] == 'f']
        if len(filled_rects) == 1:
            # We now find it's center
            rect = filled_rects[0]
            x = (int(rect['startx']) + int(rect['endx'])) // 2
            y = (int(rect['starty']) + int(rect['endy'])) // 2
        else:
            pins = self.component.pins

            # No pins? Ignore check.
            # This can be improved to include graphical items too...
            if len(pins) == 0:
                return False
            x_pos = [int(pin['posx']) for pin in pins]
            y_pos = [int(pin['posy']) for pin in pins]
            x_min = min(x_pos)
            x_max = max(x_pos)
            y_min = min(y_pos)
            y_max = max(y_pos)

            # Center point average
            x = (x_min + x_max) / 2
            y = (y_min + y_max) / 2

        # Right on the middle!
        if x == 0 and y == 0:
            return False
        elif math.fabs(x) <= 50 and math.fabs(y) <= 50:
            self.info("Symbol slightly off-center")
            self.info("  Center calculated @ ({x}, {y})".format(x=x, y=y))
        else:
            self.warning("Symbol not centered on origin")
            self.warningExtra("Center calculated @ ({x}, {y})".format(x=x, y=y))

        return False

    def fix(self):

        self.recheck()
