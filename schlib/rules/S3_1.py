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

        # Check units separately if they have different drawing ("units_locked")
        units_locked = self.component.definition['units_locked'] == 'L'
        unit_count = int(self.component.definition['unit_count']) if units_locked else 1

        for unit in range(1, unit_count+1):
            # If there is only a single filled rectangle, we assume that it is the
            # main symbol outline.
            drawing = self.component.draw
            filled_rects = [rect for rect in drawing['rectangles']
                            if ((not units_locked) or (int(rect['unit']) == unit)) and (rect['fill'] == 'f')]
            if len(filled_rects) == 1:
                # We now find it's center
                rect = filled_rects[0]
                x = (int(rect['startx']) + int(rect['endx'])) // 2
                y = (int(rect['starty']) + int(rect['endy'])) // 2
            else:
                pins = [pin for pin in self.component.pins
                        if (not units_locked) or (int(pin['unit']) == unit)]

                # No pins? Ignore check.
                # This can be improved to include graphical items too...
                if len(pins) == 0:
                    continue
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
                continue
            elif math.fabs(x) <= 50 and math.fabs(y) <= 50:
                self.info("Symbol unit {unit} slightly off-center".format(unit=unit))
                self.info("  Center calculated @ ({x}, {y})".format(x=x, y=y))
            else:
                self.warning("Symbol unit {unit} not centered on origin".format(unit=unit))
                self.warningExtra("Center calculated @ ({x}, {y})".format(x=x, y=y))

        return False

    def fix(self):

        self.recheck()
