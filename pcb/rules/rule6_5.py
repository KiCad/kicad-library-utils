# -*- coding: utf-8 -*-

from rules.rule import *
import cmath

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 6.5', 'Silkscreen is not superposed to pads, its outline is completely visible after board assembly, uses 0.15mm line width and provides a reference mark for pin 1. (IPC-7351).')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_silk
            * b_silk
            * bad_width
        """
        module = self.module
        self.f_silk = module.filterGraphs('F.SilkS')
        self.b_silk = module.filterGraphs('B.SilkS')

        # check the width
        self.bad_width = []

        for graph in (self.f_silk + self.b_silk):
            if graph['width'] != 0.15:
                self.bad_width.append(graph)

        # check intersections between line and pad, translate the line and pad
        # to coordinate (0, 0), rotate the line and pad
        self.intersections = []

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
                    edgesPad[0] = complex(pad['size']['x'] / 2, pad['size']['y'] / 2) + padComplex + padOffset
                    edgesPad[1] = complex(-pad['size']['x'] / 2, -pad['size']['y'] / 2) + padComplex + padOffset
                    edgesPad[2] = complex(pad['size']['x'] / 2, -pad['size']['y'] / 2) + padComplex + padOffset
                    edgesPad[3] = complex(-pad['size']['x'] / 2, pad['size']['y'] / 2) + padComplex + padOffset

                    vectorR = cmath.rect(1, cmath.pi / 180 * pad['pos']['orientation'])
                    for i in range(4):
                        edgesPad[i] = (edgesPad[i] - padComplex) * vectorR + padComplex

                    centerComplex = complex(graph['center']['x'], graph['center']['y'])
                    endComplex = complex(graph['end']['x'], graph['end']['y'])
                    radius = abs(endComplex - centerComplex)
                    if 'circle' in pad['shape']:
                        distance = radius + pad['size']['x'] / 2 + 0.075
                        if (abs(centerComplex - padComplex) < distance and
                            abs(centerComplex - padComplex) > abs(-radius + pad['size']['x'] / 2 + 0.075)):
                            self.intersections.append({'pad':pad, 'graph':graph})
                    else:
                        for i in range(4):
                            if abs(centerComplex - edgesPad[i]) > radius:
                                self.intersections.append({'pad':pad, 'graph':graph})
                                break
            else:
                for pad in module.pads:
                    padComplex = complex(pad['pos']['x'], pad['pos']['y'])
                    padOffset = 0 + 0j
                    if 'offset' in pad['drill']:
                        if 'x' in pad['drill']['offset']:
                            padOffset = complex(pad['drill']['offset']['x'], pad['drill']['offset']['y'])

                    edgesPad = {}
                    edgesPad[0] = complex(pad['size']['x'] / 2, pad['size']['y'] / 2) + padComplex + padOffset
                    edgesPad[1] = complex(-pad['size']['x'] / 2, -pad['size']['y'] / 2) + padComplex + padOffset
                    edgesPad[2] = complex(pad['size']['x'] / 2, -pad['size']['y'] / 2) + padComplex + padOffset
                    edgesPad[3] = complex(-pad['size']['x'] / 2, pad['size']['y'] / 2) + padComplex + padOffset

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
                        distance = cmath.sqrt((pad['size']['x'] / 2) ** 2 - (padComplex.imag) ** 2).real
                        padMinX = padComplex.real - distance
                        padMaxX = padComplex.real + distance
                    else:
                        padMinX = min(edgesPad[0].real, edgesPad[1].real, edgesPad[2].real, edgesPad[3].real)
                        padMaxX = max(edgesPad[0].real, edgesPad[1].real, edgesPad[2].real, edgesPad[3].real)

                    if ((padMinX < length and padMinX > 0) or
                        (padMaxX < length and padMaxX > 0) or
                        (padMaxX > length and padMinX < 0)) :
                        if 'circle' in pad['shape']:
                            distance = pad['size']['x'] / 2
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

        return True if (len(self.bad_width) or len(self.intersections)) else False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        from copy import deepcopy
        module = self.module

        if self.check():
            for graph in self.bad_width:
                graph['width'] = 0.15
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
                    distance = cmath.sqrt((pad['size']['x'] / 2 + 0.226) ** 2 - (padComplex.imag) ** 2).real
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
