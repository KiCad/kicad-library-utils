# -*- coding: utf-8 -*-

from __future__ import division


# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

from rules.klc_constants import *
from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, "Elements on the graphic layer should not overlap")

    def getCirclesOverlap(self,circles):
      def is_same(c1, c2):
        if c1['end'] == c2['end'] and c1['center'] == c2['center']:
          return True
        return False 
       
      overlap = []
      for c in circles:
        for c2 in circles:
          if c is c2:
            continue
          if is_same(c, c2):
            if not c in overlap:
              overlap.append(c)

      return overlap

    def getLinesOverlap(self,lines):
      # from https://stackoverflow.com/questions/328107/how-can-you-determine-a-point-is-between-two-other-points-on-a-line-segment
      def distance(a,b):
        return math.sqrt((a['x'] - b['x'])**2 + (a['y'] - b['y'])**2)

      def is_between(a,b,c):
        # check if c is the same as a or b, then c is not between a or b
        if c == b or c == a:
          return False
        # c is between a and b if in a virtual triangle the distances AC + BC = AB
        ac = distance(a,c)
        cb = distance(c,b)
        ab = distance(a,b)
        d = ac + cb - ab
        return d < 0.0001

      def is_same(l1, l2):
        if (getStartPoint(l1) == getStartPoint(l2)) and (getEndPoint(l1) == getEndPoint(l2)):
          return True
        if (getStartPoint(l1) == getEndPoint(l2)) and (getEndPoint(l1) == getStartPoint(l2)):
          return True
        return False

      overlap = []
      directions = {}
      # sort lines by colinearity
      for line in lines:
        start = getStartPoint(line)
        end = getEndPoint(line)

        if not start or not end:
          # not sure if that can happen?
          continue

        dx = start['x'] - end['x']
        dy = start['y'] - end['y']
        line['l'] = distance(start, end)
        if dx == 0:
          d = 'h'
        elif dy == 0:
          d = 'v'
        else:
          d = round(dx/dy, 3)

        if not d in directions:
          directions[d] = []
        directions[d].append(line)

      for d, lines in directions.items():
        for line in lines:
          for line2 in lines:
            if line is line2:
              continue
            if is_same(line, line2):
              if not line in overlap:
                overlap.append(line)
                lines.remove(line)
            if is_between(line['start'], line['end'], line2['start']):
              if not line in overlap:
                overlap.append(line)
                lines.remove(line)

      return overlap


    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_fabrication_lines
            * b_fabrication_lines
        """

        module = self.module
        layers_to_check = ['F.Fab', 'B.Fab', 'F.SilkS', 'B.SilkS', 'F.CrtYd', 'B.CrtYd']

        self.overlaps = {}
        self.errcnt = 0
        for layer in layers_to_check:
            self.overlaps[layer] = []
            self.overlaps[layer].extend(self.getLinesOverlap(module.filterLines(layer)))
            self.overlaps[layer].extend(self.getCirclesOverlap(module.filterCircles(layer)))

            # Display message if silkscreen has overlapping lines
            if len(self.overlaps[layer]) > 0:
                self.errcnt += 1
                self.error("%s graphic elements should not overlap." % layer)
                self.errorExtra("The following elements do overlap at least one other graphic element on the same layer")
                for bad in self.overlaps[layer]:
                    self.errorExtra(graphItemString(bad, layer=True, width=False))

        return self.errcnt > 0

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        return
