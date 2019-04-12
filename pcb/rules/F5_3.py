# -*- coding: utf-8 -*-

from __future__ import division

# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

from rules.rule import *
import re, os, math

from rules.klc_constants import *

import sys
sys.path.append(os.path.join('..','..','common'))

from boundingbox import BoundingBox

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, "Courtyard layer requirements")

    # Get the superposed boundary of pads and fab layer
    def getFootprintBounds(self):
        module = self.module

        padBounds = module.overpadsBounds()

        # Try getting bounds from these layers, in order
        layers = ['F.Fab', 'B.Fab', 'F.SilkS', 'B.SilkS']

        # Accept first valid layer
        for layer in layers:
            geo = module.geometricBoundingBox(layer)
            if geo.valid:
                print("using drawing from layer", layer)
                break

        # Add two bounding boxes together
        padBounds.addBoundingBox(geo)

        return padBounds

    # Return best-guess for courtyard offset
    def defaultOffset(self):
        module = self.module
        module_dir = os.path.split(os.path.dirname(os.path.realpath(module.filename)))[-1]
        self.module_dir = "{0}".format(os.path.splitext(module_dir))

        # Default offset
        offset = 0.25

        bb=self.getFootprintBounds()

        # Smaller offset for miniature components
        if bb.width < 2 and bb.height < 2:
            offset = 0.15

        # BGA components required 1.0mm clearance
        if re.match("BGA\-.*", module.name) or re.match(".*Housing.*BGA.*", module_dir):
            offset = 1

        # Connectors require 0.5mm clearance
        elif re.match(".*Connector.*", module.name) or \
             re.match(".*Connector.*", self.module_dir) or \
             re.match(".*Socket.*", module.name) or \
             re.match(".*Socket.*", self.module_dir) or \
             re.match(".*Button.*", module.name) or \
             re.match(".*Button.*", self.module_dir) or \
             re.match(".*Switch.*", module.name) or \
             re.match(".*Switch.*", self.module_dir):
            offset = 0.5

        return offset

    def defaultCourtyard(self):
        bb = self.getFootprintBounds()

        offset = self.defaultOffset()

        bb.expand(offset)

        print("Offset:", offset)

        if bb.valid:
            return {
                'x': mapToGrid(bb.xmin, KLC_CRTYD_GRID),
                'y': mapToGrid(bb.ymin, KLC_CRTYD_GRID),
                'width':  mapToGrid(bb.width, KLC_CRTYD_GRID),
                'height': mapToGrid(bb.height, KLC_CRTYD_GRID),
                }

        # No valid bounding box found in component
        else:
            return None


    def isClosed(self, layer):
      def isSame(p1, p2, tolerance):
        s = abs(p1['x'] - p2['x']) <= tolerance and abs(p1['y'] - p2['y']) <= tolerance
        return s

      # no line is considered as closed
      if len(layer) == 0:
        return []

      # clone the lines, so we can remove them from the list
      lines = layer[0:]
      curr_line = lines.pop()
      curr_point = getStartPoint(curr_line)
      end_point = getEndPoint(curr_line)
      tolerance = 0

      while len(lines) > 0:
        tolerance = 0
        match = False
        for line in lines:
          if 'angle' in line or 'angle' in curr_line:
            tolerance = 0.01
          if isSame(curr_point, getStartPoint(line), tolerance):
            curr_line = line
            curr_point = getEndPoint(line)
            lines.remove(line)
            match = True
            break
          if isSame(curr_point, getEndPoint(line), tolerance):
            curr_line = line
            curr_point = getStartPoint(line)
            lines.remove(line)
            match = True
            break
        # we should hit a continue
        # if now, that means no line connects
        if not match:
          return [curr_line]
      # now check the if the last points match
      if isSame(curr_point, end_point, tolerance):
        return []
      else:
        return [curr_line]

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_courtyard_all
            * b_courtyard_all
            * f_courtyard_lines
            * b_courtyard_lines
            * bad_width
            * bad_grid
            * crt_offset
            * actual_crt_rectangle
            * expected_crt_rectangle
            * courtyard_rectangle_layer
        """

        error = False

        module = self.module

        self.bad_grid  = []
        self.bad_width = []
        self.unconnected = []

        self.fCourtyard = module.filterGraphs('F.CrtYd')
        self.bCourtyard = module.filterGraphs('B.CrtYd')

        # Check for existence of courtyard
        if len(self.fCourtyard) == 0:
            if len(self.bCourtyard) == 0:
                self.error("No courtyard found!")
                self.errorExtra("Add courtyard around footprint")
                return True

        self.courtyard = self.fCourtyard + self.bCourtyard

        GRID = int(KLC_CRTYD_GRID * 1E6)

        # Check for intersecting lines
        self.unconnected.extend(self.isClosed(self.fCourtyard))
        self.unconnected.extend(self.isClosed(self.bCourtyard))

        for graph in self.courtyard:
            if graph['width'] != KLC_CRTYD_WIDTH:
                self.bad_width.append(graph)

            start = getStartPoint(graph)
            end = getEndPoint(graph)

            if not start or not end:
                self.bad_grid.append(graph)
                continue

            x1 = mmToMicrons(start['x'])
            y1 = mmToMicrons(start['y'])

            x2 = mmToMicrons(end['x'])
            y2 = mmToMicrons(end['y'])

            check = [x1, y2, x2, y2]

            grid_error = False
            for c in check:
                if not (c % GRID) == 0:
                    grid_error = True
                    break
            if grid_error:
                self.bad_grid.append(graph)

        # Check that courtyard is correct width
        if len(self.bad_width) > 0:
            self.error("Courtyard width error (expected width = {w}mm)".format(
                w = KLC_CRTYD_WIDTH))
            for bad in self.bad_width:
                self.errorExtra(graphItemString(bad, layer=True, width=True))

        # Check that courtyard items are on correct grid
        if len(self.bad_grid) > 0:
            self.error("Courtyard lines are not on {grid}mm grid".format(
                grid = KLC_CRTYD_GRID))
            for bad in self.bad_grid:
                self.errorExtra(graphItemString(bad, layer=True, width=False))

        # Check that courtyard is closed
        if len(self.unconnected) > 0:
            self.error("Courtyard must be closed.")
            self.errorExtra("The following lines have unconnected endpoints")
            for bad in self.unconnected:
                self.errorExtra(graphItemString(bad, layer=True, width=False))

        return any([
            len(self.bad_width) > 0,
            len(self.bad_grid) > 0,
            len(self.unconnected) > 0
            ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module

        if len(self.bad_width) > 0:
            self.info("Fixing line width of courtyard items")
        for graph in self.bad_width:
            graph['width'] = KLC_CRTYD_WIDTH

        if len(self.bad_grid) > 0:
            self.info("Fixing grid alignment of courtyard items")
        for item in self.bad_grid:
            if 'center' in item: # Circle
                key = 'center'
            else:                # Lines, Arcs
                key = 'start'

            item[key]['x'] = mapToGrid(item[key]['x'], KLC_CRTYD_GRID)
            item[key]['y'] = mapToGrid(item[key]['y'], KLC_CRTYD_GRID)

            item['end']['x'] = mapToGrid(item['end']['x'], KLC_CRTYD_GRID)
            item['end']['y'] = mapToGrid(item['end']['y'], KLC_CRTYD_GRID)

        # create courtyard if does not exists
        if len(self.fCourtyard) + len(self.bCourtyard) == 0:
            self.info("No courtyard detected - adding default courtyard")
            cy = self.defaultCourtyard()
            if not cy:
                self.info("Could not add courtyard - no footprint items found")
            else:
                self.module.addRectangle(
                    [cy['x'], cy['y']],
                    [cy['x'] + cy['width'], cy['y'] + cy['height']],
                    'F.CrtYd', KLC_CRTYD_WIDTH)