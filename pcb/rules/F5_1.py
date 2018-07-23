# -*- coding: utf-8 -*-

from __future__ import division

from rules.rule import *
from rules.klc_constants import *
import cmath

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, "Silkscreen layer requirements")

    def checkReference(self):
        """
        Check that the RefDes is included on the silkscreen layer,
        and has the correct dimensions (etc)
        """

        module = self.module

        ref = module.reference

        font = ref['font']

        errors = []

        # Check correct value of reference field
        if not ref['reference'] == 'REF**':
            errors.append("Reference text is '{v}', expected: 'REF**'".format(
                v = ref['reference']))

        # Check correct layer for reference
        if ref['layer'] not in ['F.SilkS', 'B.SilkS']:
            errors.append("Reference label is on layer '{0}', but should be on layer F.SilkS or B.SilkS!".format(ref['layer']))

        # Check that reference is not hidden
        if ref['hide']:
            errors.append("Reference label is hidden (must be set to visible)")

        # Check reference size
        if not font['width'] == font['height']:
            errors.append("Reference label font aspect ratio should be 1:1")
        if font['height'] !=  KLC_TEXT_SIZE:
            errors.append("Reference label has a height of {1}mm (expected: {0}mm).".format(KLC_TEXT_SIZE,font['height']))
        if font['width'] != KLC_TEXT_SIZE:
            errors.append("Reference label has a width of {1}mm (expected: {0}mm).".format(KLC_TEXT_SIZE,font['width']))
        if font['thickness'] != KLC_TEXT_THICKNESS:
            errors.append("Reference label has a thickness of {1}mm (expected: {0}mm).".format(KLC_TEXT_THICKNESS,font['thickness']))

        self.refDesError = len(errors) > 0

        if len(errors) > 0:
            self.error("Reference label errors:")
            for err in errors:
                self.errorExtra(err)

    """
    Check that all silkscreen lines are of the correct width
    """
    def checkSilkscreenWidth(self):
        # check the width
        self.bad_width = []
        self.non_nominal_width = []

        for graph in (self.f_silk + self.b_silk):
            if graph['width'] not in KLC_SILK_WIDTH_ALLOWED:
                self.bad_width.append(graph)
            elif graph['width'] != KLC_SILK_WIDTH:
                self.non_nominal_width.append(graph)

    """
    Check if any of the silkscreen intersects
    with pads, etc
    """
    def checkIntersections(self):

        module = self.module

        for graph in (self.f_silk + self.b_silk):
            if 'angle' in graph:
                #TODO
                pass
            elif 'center' in graph:
                for pad in module.pads:
                    padComplex = complex(pad['pos']['x'], pad['pos']['y'])
                    padOffset = 0 + 0j
                    if 'offset' in pad['drill']:
                        if 'x' in pad['drill']['offset']:
                            padOffset = complex(pad['drill']['offset']['x'], pad['drill']['offset']['y'])

                    edgesPad = {}
                    edgesPad[0] = complex(pad['size']['x'] / 2.0, pad['size']['y'] / 2.0) + padComplex + padOffset
                    edgesPad[1] = complex(-pad['size']['x'] / 2.0, -pad['size']['y'] / 2.0) + padComplex + padOffset
                    edgesPad[2] = complex(pad['size']['x'] / 2.0, -pad['size']['y'] / 2.0) + padComplex + padOffset
                    edgesPad[3] = complex(-pad['size']['x'] / 2.0, pad['size']['y'] / 2.0) + padComplex + padOffset

                    vectorR = cmath.rect(1, cmath.pi / 180 * pad['pos']['orientation'])
                    for i in range(4):
                        edgesPad[i] = (edgesPad[i] - padComplex) * vectorR + padComplex

                    centerComplex = complex(graph['center']['x'], graph['center']['y'])
                    endComplex = complex(graph['end']['x'], graph['end']['y'])
                    radius = abs(endComplex - centerComplex)
                    if 'circle' in pad['shape']:
                        distance = radius + pad['size']['x'] / 2.0 + 0.075
                        if (abs(centerComplex - padComplex) < distance and
                            abs(centerComplex - padComplex) > abs(-radius + pad['size']['x'] / 2.0 + 0.075)):
                            self.intersections.append({'pad':pad, 'graph':graph})
                    else:
                        # if there are edges inside and outside the circle, we have an intersection
                        edgesInside = []
                        edgesOutside = []
                        for i in range(4):
                            if abs(centerComplex - edgesPad[i]) < radius:
                                edgesInside.append(edgesPad[i])
                            else:
                                edgesOutside.append(edgesPad[i])
                        if edgesInside and edgesOutside:
                            self.intersections.append({'pad':pad, 'graph':graph})
            else:
                for pad in module.pads:

                    # Skip checks on NPTH and Connect holes
                    if pad['type'] in ['np_thru_hole', 'connect']:
                        continue

                    padComplex = complex(pad['pos']['x'], pad['pos']['y'])
                    padOffset = 0 + 0j
                    if 'offset' in pad['drill']:
                        if 'x' in pad['drill']['offset']:
                            padOffset = complex(pad['drill']['offset']['x'], pad['drill']['offset']['y'])

                    edgesPad = {}
                    edgesPad[0] = complex(pad['size']['x'] / 2.0, pad['size']['y'] / 2.0) + padComplex + padOffset
                    edgesPad[1] = complex(-pad['size']['x'] / 2.0, -pad['size']['y'] / 2.0) + padComplex + padOffset
                    edgesPad[2] = complex(pad['size']['x'] / 2.0, -pad['size']['y'] / 2.0) + padComplex + padOffset
                    edgesPad[3] = complex(-pad['size']['x'] / 2.0, pad['size']['y'] / 2.0) + padComplex + padOffset

                    vectorR = cmath.rect(1, cmath.pi / 180 * pad['pos']['orientation'])
                    for i in range(4):
                        edgesPad[i] = (edgesPad[i] - padComplex) * vectorR + padComplex

                    startComplex = complex(graph['start']['x'], graph['start']['y'])
                    endComplex = complex(graph['end']['x'], graph['end']['y'])
                    if endComplex.imag > startComplex.imag:
                        vector = endComplex - startComplex
                        padComplex = padComplex - startComplex
                        for i in range(4):
                            edgesPad[i] = edgesPad[i] - startComplex
                    else:
                        vector = startComplex - endComplex
                        padComplex = padComplex - endComplex
                        for i in range(4):
                            edgesPad[i] = edgesPad[i] - endComplex
                    length = abs(vector)

                    vectorR = cmath.rect(1, -cmath.phase(vector))
                    padComplex = padComplex * vectorR
                    for i in range(4):
                            edgesPad[i] = edgesPad[i] * vectorR

                    if 'circle' in pad['shape']:
                        distance = cmath.sqrt((pad['size']['x'] / 2.0) ** 2 - (padComplex.imag) ** 2).real
                        padMinX = padComplex.real - distance
                        padMaxX = padComplex.real + distance
                    else:
                        edges = [[0,3],[0,2],[2,1],[1,3]] #lines of the rectangle pads
                        x0 = [] #vector of value the x to y=0
                        for edge in edges:
                            x1 = edgesPad[edge[0]].real
                            x2 = edgesPad[edge[1]].real
                            y1 = edgesPad[edge[0]].imag
                            y2 = edgesPad[edge[1]].imag
                            if y1 != y2:
                                x = -y1 / (y2 - y1) * (x2 - x1) + x1
                                if x < max(x1, x2) and x > min(x1, x2):
                                    x0.append(x)
                        if x0:
                            padMinX = min(x0)
                            padMaxX = max(x0)
                        else:
                            continue
                    if ((padMinX < length and padMinX > 0) or
                        (padMaxX < length and padMaxX > 0) or
                        (padMaxX > length and padMinX < 0)) :
                        if 'circle' in pad['shape']:
                            distance = pad['size']['x'] / 2.0
                            padMin = padComplex.imag - distance
                            padMax = padComplex.imag + distance
                        else:
                            padMin = min(edgesPad[0].imag, edgesPad[1].imag, edgesPad[2].imag, edgesPad[3].imag)
                            padMax = max(edgesPad[0].imag, edgesPad[1].imag, edgesPad[2].imag, edgesPad[3].imag)
                        try:
                            differentSign = padMax / padMin
                        except:
                            differentSign = padMin / padMax
                        if (differentSign < 0) or (abs(padMax) < 0.075) or (abs(padMin) < 0.075):
                            self.intersections.append({'pad':pad, 'graph':graph})

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_silk
            * b_silk
            * bad_width
            * non_nominal_width
        """
        module = self.module
        self.f_silk = module.filterGraphs('F.SilkS')
        self.b_silk = module.filterGraphs('B.SilkS')

        self.checkReference()
        self.checkSilkscreenWidth()

        # check intersections between line and pad, translate the line and pad
        # to coordinate (0, 0), rotate the line and pad
        self.intersections = []

        self.checkIntersections()

        # Display message if bad silkscreen width was found
        if self.bad_width:
            self.error("Some silkscreen lines have incorrect width: Allowed "
                       "= {allowed} mm".format(allowed=KLC_SILK_WIDTH_ALLOWED))
            for g in self.bad_width:
                self.errorExtra(graphItemString(g, layer=True, width=True))

        if self.non_nominal_width:
            self.warning("Some silkscreen lines are not using the nominal "
                         "width of {width} mm".format(width=KLC_SILK_WIDTH))
            for g in self.non_nominal_width:
                self.warningExtra(graphItemString(g, layer=True, width=True))

        # Display message if silkscreen was found intersecting with pad
        if self.intersections:
            self.error("Some Silkscreen lines intersects with pads")
            pad_nums = []
            for ints in self.intersections:
                if not ints['pad']['number'] in pad_nums:
                    self.errorExtra(" - Pad {n} @ ({x},{y})".format(
                        n = ints['pad']['number'],
                        x = ints['pad']['pos']['x'],
                        y = ints['pad']['pos']['y']))
                    pad_nums.append(ints['pad']['number'])

        # Return True if any of the checks returned an error
        return any([len(self.bad_width) > 0,
                    len(self.intersections) > 0,
                    self.refDesError
                    ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        from copy import deepcopy
        module = self.module

        if self.check():
            if self.refDesError:
                ref = self.module.reference
                if self.checkReference():
                    ref['value'] = 'REF**'
                    ref['layer'] = 'F.SilkS'
                    ref['font']['width'] = KLC_TEXT_WIDTH
                    ref['font']['height'] = KLC_TEXT_HEIGHT
                    ref['font']['thickness'] = KLC_TEXT_THICKNESS
            for graph in self.bad_width:
                graph['width'] = KLC_SILK_WIDTH
            for inter in self.intersections:
                pad = inter['pad']
                graph = inter['graph']
                if 'angle' in graph:
                    #TODO
                    pass
                elif 'center' in graph:
                    #TODO
                    pass
                else:
                    padComplex = complex(pad['pos']['x'], pad['pos']['y'])
                    startComplex = complex(graph['start']['x'], graph['start']['y'])
                    endComplex = complex(graph['end']['x'], graph['end']['y'])
                    if endComplex.imag < startComplex.imag:
                        tmp = endComplex
                        endComplex = startComplex
                        startComplex = tmp
                        graph['start']['x'] = startComplex.real
                        graph['start']['y'] = startComplex.imag
                        graph['end']['x'] = endComplex.real
                        graph['end']['y'] = endComplex.imag

                    vector = endComplex - startComplex
                    padComplex = padComplex - startComplex
                    length = abs(vector)
                    phase = cmath.phase(vector)
                    vectorR = cmath.rect(1, -phase)
                    padComplex = padComplex * vectorR
                    distance = cmath.sqrt((pad['size']['x'] / 2.0 + 0.226) ** 2 - (padComplex.imag) ** 2).real
                    padMin = padComplex.real - distance
                    padMax = padComplex.real + distance

                    if padMin < length and padMin > 0:
                        if padMax > length:
                            padComplex = (padMin + 0j) * cmath.rect(1, phase) + startComplex
                            graph['end']['x'] = round(padComplex.real, 3)
                            graph['end']['y'] = round(padComplex.imag, 3)
                        else:
                            padComplex = (padMin + 0j) * cmath.rect(1, phase) + startComplex
                            graph2 = deepcopy(graph)
                            graph['end']['x'] = round(padComplex.real, 3)
                            graph['end']['y'] = round(padComplex.imag, 3)
                            padComplex = (padMax + 0j) * cmath.rect(1, phase) + startComplex
                            graph2['start'].update({'x':round(padComplex.real, 3)})
                            graph2['start'].update({'y':round(padComplex.imag, 3)})
                            module.lines.append(graph2)
                    elif padMin < 0 and padMax > 0 and padMax < length:
                        padComplex = (padMax + 0j) * cmath.rect(1, phase) + startComplex
                        graph['start']['x'] = round(padComplex.real, 3)
                        graph['start']['y'] = round(padComplex.imag, 3)
                    elif (padMax > length and padMin < 0):
                        module.lines.remove(graph)
