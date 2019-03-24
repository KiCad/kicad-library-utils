#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import time
import re, math
import sys, os
sys.path.append(os.path.join('..','common'))

import sexpr
from boundingbox import BoundingBox

# Rotate a point by given angle (in degrees)
def _rotatePoint(point, degrees):

    # Create a new point (copy)
    p = {}
    for key in point:
        p[key] = point[key]

    radians = degrees * math.pi / 180

    x = point['x']
    y = point['y']

    p['x'] = x * math.cos(radians) - y * math.sin(radians)
    p['y'] = y * math.cos(radians) + x * math.sin(radians)

    if 'orientation' in point:
        p['orientation'] -= degrees

    return p

# Move point by certain offset
def _movePoint(point, offset):

    # Copy all points

    p = {}
    for key in point:
        p[key] = point[key]

    p['x'] += offset['x']
    p['y'] += offset['y']

    return p

class KicadMod(object):
    """
    A class to parse kicad_mod files format of the KiCad
    """
    def __init__(self, filename):
        self.filename = filename

        # read the s-expression data
        f = open(filename)
        sexpr_data = ''.join(f.readlines())

        # parse s-expr
        sexpr_data = sexpr.parse_sexp(sexpr_data)
        self.sexpr_data = sexpr_data

        # module name
        self.name = self.sexpr_data[1]

        # module layer
        self.layer = self._getValue('layer', 'pth', 2)

        # locked flag
        self.locked = self._getValue('locked', False, 2)

        # description
        self.description = self._getValue('descr', '', 2)

        # tags
        self.tags = self._getValue('tags', '', 2)

        # auto place settings
        self.autoplace_cost90 = self._getValue('autoplace_cost90', 0, 2)
        self.autoplace_cost180 = self._getValue('autoplace_cost180', 0, 2)

        # global footprint clearance settings
        self.clearance = self._getValue('clearance', 0, 2)
        self.solder_mask_margin = self._getValue('solder_mask_margin', 0, 2)
        self.solder_paste_margin = self._getValue('solder_paste_margin', 0, 2)
        self.solder_paste_ratio = self._getValue('solder_paste_ratio', 0, 2)

        # attribute
        self.attribute =  self._getValue('attr', 'pth', 2)

        # reference
        self.reference = self._getText('reference')[0]

        # value
        self.value = self._getText('value')[0]

        # user text
        self.userText = self._getText('user')

        # lines
        self.lines = self._getLines()

        # circles
        self.circles = self._getCircles()

        # arcs
        self.arcs = self._getArcs()

        # pads
        self.pads = self._getPads()

        # models
        self.models = self._getModels()

    # check if value exists in any element of data
    def _hasValue(self, data, value):
        for i in data:
            if type(i) in [list, tuple]:
                if self._hasValue(i, value):
                    return True
            elif str(i) == value:
                return True
        return False

    # return the array which has value as first element
    def _getArray(self, data, value, result=None, level=0, max_level = None):
        if result is None: result = []

        if max_level is not None and max_level <= level:
            return result

        level += 1

        for i in data:
            if type(i) == type([]):
                self._getArray(i, value, result, level=level,
                        max_level=max_level)
            else:
                if i == value:
                    result.append(data)
        return result

    # update or create an array
    def _updateCreateArray(self, array, place_after=None):
        # check if array exists
        # first element of array is used as key
        # this function only works for arrays which has a single occurrence
        found_array = self._getArray(self.sexpr_data, array[0])
        if found_array:
            index = self.sexpr_data.index(found_array[0])
            self.sexpr_data.pop(index)
            self.sexpr_data.insert(index, array)
        else:
            self._createArray(array, place_after)

    # create an array
    def _createArray(self, new_array, place_after=None):
        # place_after must be an array with the desired position name
        # once the first name match the new array will be placed after
        # the last matched occurrence of the name
        for field in place_after:
            pos_array = self._getArray(self.sexpr_data, field)
            if pos_array:
                index = len(self.sexpr_data) - self.sexpr_data[::-1].index(pos_array[-1]) - 1
                self.sexpr_data.insert(index + 1, new_array)
                break
        else:
            # case doesn't find any desired position, append to end of the array
            self.sexpr_data.append(new_array)

    # return the second element of the array because the array is expected
    # to have the following format: [key value]
    # returns def_value if not field the value
    def _getValue(self, array, def_value=None, max_level=None):
        a = self._getArray(self.sexpr_data, array, max_level=max_level)
        return def_value if not a else a[0][1]

    def _getText(self, which_text):
        result = []
        for text in self._getArray(self.sexpr_data, 'fp_text'):
            if text[1] == which_text:
                text_dict = {}
                text_dict[which_text] = text[2]

                # text position
                a = self._getArray(text, 'at')[0]
                text_dict['pos'] = {'x':a[1], 'y':a[2], 'orientation':0}
                if len(a) > 3: text_dict['pos']['orientation'] = a[3]

                # text layer
                a = self._getArray(text, 'layer')[0]
                text_dict['layer'] = a[1]

                # text font
                font = self._getArray(text, 'font')[0]

                # Some footprints miss out some parameters
                text_dict['font'] = {'thickness': 0, 'height': 0, 'width': 0}

                for pair in font[1:]:
                    key = pair[0]
                    data = pair[1:]

                    if key == 'thickness':
                        text_dict['font']['thickness'] = data[0]

                    elif key == 'size':
                        text_dict['font']['height'] = data[0]
                        text_dict['font']['width'] = data[1]

                text_dict['font']['italic'] = self._hasValue(a, 'italic')

                # text hide
                text_dict['hide'] = self._hasValue(text, 'hide')

                result.append(text_dict)

        return result

    def addUserText(self, text, params):
        user = {'user': text}
        for key in params:
            user[key] = params[key]

        self.userText.append(user)

    def _getLines(self, layer=None):
        lines = []
        for line in self._getArray(self.sexpr_data, 'fp_line'):
            line_dict = {}
            if self._hasValue(line, layer) or layer == None:
                a = self._getArray(line, 'start')[0]
                line_dict['start'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(line, 'end')[0]
                line_dict['end'] = {'x':a[1], 'y':a[2]}

                try:
                    a = self._getArray(line, 'layer')[0]
                    line_dict['layer'] = a[1]
                except:
                    line_dict['layer'] = ''

                try:
                    a = self._getArray(line, 'width')[0]
                    line_dict['width'] = a[1]
                except:
                    line_dict['width'] = 0

                lines.append(line_dict)

        return lines

    def _getCircles(self, layer=None):
        circles = []
        for circle in self._getArray(self.sexpr_data, 'fp_circle'):
            circle_dict = {}
            # filter layers, None = all layers
            if self._hasValue(circle, layer) or layer == None:
                a = self._getArray(circle, 'center')[0]
                circle_dict['center'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(circle, 'end')[0]
                circle_dict['end'] = {'x':a[1], 'y':a[2]}

                try:
                    a = self._getArray(circle, 'layer')[0]
                    circle_dict['layer'] = a[1]
                except:
                    circle_dict['layer'] = ''

                try:
                    a = self._getArray(circle, 'width')[0]
                    circle_dict['width'] = a[1]
                except:
                    circle_dict['width'] = 0

                circles.append(circle_dict)

        return circles

    def _getArcs(self, layer=None):
        arcs = []
        for arc in self._getArray(self.sexpr_data, 'fp_arc'):
            arc_dict = {}
            # filter layers, None = all layers
            if self._hasValue(arc, layer) or layer == None:
                a = self._getArray(arc, 'start')[0]
                arc_dict['start'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(arc, 'end')[0]
                arc_dict['end'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(arc, 'angle')[0]
                arc_dict['angle'] = a[1]

                try:
                    a = self._getArray(arc, 'layer')[0]
                    arc_dict['layer'] = a[1]
                except:
                    arc_dict['layer'] = ''

                try:
                    a = self._getArray(arc, 'width')[0]
                    arc_dict['width'] = a[1]
                except:
                    arc_dict['width'] = 0

                arcs.append(arc_dict)

        return arcs

    def _getPads(self):
        pads = []
        for pad in self._getArray(self.sexpr_data, 'pad'):
            # number, type, shape
            pad_dict = {'number':pad[1], 'type':pad[2], 'shape':pad[3]}

            # position
            a = self._getArray(pad, 'at')[0]
            pad_dict['pos'] = {'x':a[1], 'y':a[2], 'orientation':0}
            if len(a) > 3: pad_dict['pos']['orientation'] = a[3]

            # size
            a = self._getArray(pad, 'size')[0]
            pad_dict['size'] = {'x':a[1], 'y':a[2]}

            # layers
            a = self._getArray(pad, 'layers')[0]
            pad_dict['layers'] = a[1:]

            # rect delta
            pad_dict['rect_delta'] = {}
            a = self._getArray(pad, 'rect_delta')
            if a: pad_dict['rect_delta'] = a[0][1:]

            # drill
            pad_dict['drill'] = {}
            drill = self._getArray(pad, 'drill')
            if drill:
                # there is only one drill per pad
                drill = drill[0]

                # offset
                pad_dict['drill']['offset'] = {}
                offset = self._getArray(drill, 'offset')
                if offset:
                    offset = offset[0]
                    pad_dict['drill']['offset'] = {'x':offset[1], 'y':offset[2]}
                    drill.remove(offset)

                # shape
                if self._hasValue(drill, 'oval'):
                    drill.remove('oval')
                    pad_dict['drill']['shape'] = 'oval'
                else:
                    pad_dict['drill']['shape'] = 'circular'

                # size
                pad_dict['drill']['size'] = {}
                if len(drill) > 1:
                    x = drill[1]
                    y = drill[2] if len(drill) > 2 else x
                    pad_dict['drill']['size'] = {'x':x, 'y':y}

            # die length
            pad_dict['die_length'] = {}
            a = self._getArray(pad, 'die_length')
            if a: pad_dict['die_length'] = a[0][1]

            ## clearances zones settings
            # clearance
            pad_dict['clearance'] = {}
            a = self._getArray(pad, 'clearance')
            if a: pad_dict['clearance'] = a[0][1]
            # solder mask margin
            pad_dict['solder_mask_margin'] = {}
            a = self._getArray(pad, 'solder_mask_margin')
            if a: pad_dict['solder_mask_margin'] = a[0][1]
            # solder paste margin
            pad_dict['solder_paste_margin'] = {}
            a = self._getArray(pad, 'solder_paste_margin')
            if a: pad_dict['solder_paste_margin'] = a[0][1]
            # solder paste margin ratio
            pad_dict['solder_paste_margin_ratio'] = {}
            a = self._getArray(pad, 'solder_paste_margin_ratio')
            if a: pad_dict['solder_paste_margin_ratio'] = a[0][1]

            ## copper zones settings
            # zone connect
            pad_dict['zone_connect'] = {}
            a = self._getArray(pad, 'zone_connect')
            if a: pad_dict['zone_connect'] = a[0][1]
            # thermal width
            pad_dict['thermal_width'] = {}
            a = self._getArray(pad, 'thermal_width')
            if a: pad_dict['thermal_width'] = a[0][1]
            # thermal gap
            pad_dict['thermal_gap'] = {}
            a = self._getArray(pad, 'thermal_gap')
            if a: pad_dict['thermal_gap'] = a[0][1]

            # Custom pad shape settings
            if pad_dict['shape'] == 'custom':
                # Get options
                pad_dict['options'] = {'clearance': {}, 'anchor': {}}
                a = self._getArray(pad, 'options')
                c = self._getArray(a, 'clearance')
                if c:
                    pad_dict['options']['clearance'] = c[0][1]
                c = self._getArray(a, 'anchor')
                if c:
                    pad_dict['options']['anchor'] = c[0][1]

                # Get primitives
                pad_dict['primitives'] = []
                a = self._getArray(pad, 'primitives')
                if a:
                    for primitive in a[0][1:]:
                        p = {}
                        # Everything has a width
                        p['width'] = {}
                        w = self._getArray(primitive, 'width')
                        if w: p['width'] = w[0][1]
                        # Set primitive type
                        p['type'] = primitive[0]
                        if primitive[0] == 'gr_poly':
                            # Read the polygon's points
                            p['pts'] = []
                            pts = self._getArray(primitive, 'pts')
                            for pt in pts[0][1:]:
                                p['pts'].append({
                                    'x': pt[1],
                                    'y': pt[2]})
                        elif primitive[0] == 'gr_line':
                            # Read the line's start
                            p['start'] = {}
                            s = self._getArray(primitive, 'start')
                            if s: p['start'] = {'x': s[0][1], 'y': s[0][2]}
                            # Read the line's end
                            p['end'] = {}
                            e = self._getArray(primitive, 'end')
                            if e: p['end'] = {'x': e[0][1], 'y': e[0][2]}
                        elif primitive[0] == 'gr_arc':
                            # Read the arc's start
                            p['start'] = {}
                            s = self._getArray(primitive, 'start')
                            if s: p['start'] = {'x': s[0][1], 'y': s[0][2]}
                            # Read the arc's end
                            p['end'] = {}
                            e = self._getArray(primitive, 'end')
                            if e: p['end'] = {'x': e[0][1], 'y': e[0][2]}
                            # Read the arc's angle
                            p['angle'] = {}
                            n = self._getArray(primitive, 'angle')
                            if n: p['angle'] = n[0][1]
                        elif primitive[0] == 'gr_circle':
                            # Read the line's start
                            p['center'] = {}
                            c = self._getArray(primitive, 'center')
                            if c: p['center'] = {'x': c[0][1], 'y': c[0][2]}
                            # Read the line's end
                            p['end'] = {}
                            e = self._getArray(primitive, 'end')
                            if e: p['end'] = {'x': e[0][1], 'y': e[0][2]}

                        pad_dict['primitives'].append(p)

            pads.append(pad_dict)

        return pads

    def _getModels(self):
        models_array = self._getArray(self.sexpr_data, 'model')

        models = []
        for model in models_array:
            model_dict = {'file':model[1]}

            # position
            offset = self._getArray(model, 'at')
            if len(offset) < 1:
                offset = self._getArray(model, 'offset')
            xyz = self._getArray(offset, 'xyz')[0]
            model_dict['pos'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            # scale
            xyz = self._getArray(self._getArray(model, 'scale'), 'xyz')[0]
            model_dict['scale'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            # rotate
            xyz = self._getArray(self._getArray(model, 'rotate'), 'xyz')[0]
            model_dict['rotate'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            models.append(model_dict)

        return models

    # Add a 3D model
    def addModel(self, filename, pos=[0,0,0], scale=[1,1,1], rotate=[0,0,0]):
        model_dict = {'file':filename}
        # position
        model_dict['pos'] = {'x':pos[0], 'y':pos[1], 'z':pos[2]}
        # scale
        model_dict['scale'] = {'x':scale[0], 'y':scale[1], 'z':scale[2]}
        # rotate
        model_dict['rotate'] = {'x':rotate[0], 'y':rotate[1], 'z':rotate[2]}
        self.models.append(model_dict)

    def addLine(self, start, end, layer, width):
        line={
               'start': {'x': start[0], 'y': start[1]},
               'end': {'x': end[0], 'y': end[1]},
               'layer': layer,
               'width': width
             }
        self.lines.append( line)

    def addRectangle(self, start, end, layer, width):
        self.addLine( [ start[0], start[1] ], [ end[0], start[1] ], layer, width)
        self.addLine( [ start[0], start[1] ], [ start[0], end[1] ], layer, width)
        self.addLine( [ end[0], end[1] ], [ end[0], start[1] ], layer, width)
        self.addLine( [ end[0], end[1] ], [ start[0], end[1] ], layer, width)


    def setAnchor(self, anchor_point):
        # change reference position
        self.reference['pos']['x'] -= anchor_point[0]
        self.reference['pos']['y'] -= anchor_point[1]

        # change value position
        self.value['pos']['x'] -= anchor_point[0]
        self.value['pos']['y'] -= anchor_point[1]

        # change user text position
        for text in self.userText:
            text['pos']['x'] -= anchor_point[0]
            text['pos']['y'] -= anchor_point[1]

        # change lines position
        for line in self.lines:
            line['start']['x'] -= anchor_point[0]
            line['end']['x'] -= anchor_point[0]
            line['start']['y'] -= anchor_point[1]
            line['end']['y'] -= anchor_point[1]

        # change circles position
        for circle in self.circles:
            circle['center']['x'] -= anchor_point[0]
            circle['end']['x'] -= anchor_point[0]
            circle['center']['y'] -= anchor_point[1]
            circle['end']['y'] -= anchor_point[1]

        # change arcs position
        for arc in self.arcs:
            arc['start']['x'] -= anchor_point[0]
            arc['end']['x'] -= anchor_point[0]
            arc['start']['y'] -= anchor_point[1]
            arc['end']['y'] -= anchor_point[1]

        # change pads positions
        for pad in self.pads:
            pad['pos']['x'] -= anchor_point[0]
            pad['pos']['y'] -= anchor_point[1]

        # change models
        for model in self.models:
            model['pos']['x'] -= anchor_point[0]/25.4
            model['pos']['y'] += anchor_point[1]/25.4



    def rotateFootprint(self, degrees):
        # change reference position
        self.reference['pos']=_rotatePoint(self.reference['pos'], degrees)

        # change value position
        self.value['pos']=_rotatePoint(self.value['pos'], degrees)

        # change user text position
        for text in self.userText:
            text['pos']=_rotatePoint(text['pos'], degrees)


        # change lines position
        for line in self.lines:
            line['start']=_rotatePoint(line['start'], degrees)
            line['end']=_rotatePoint(line['end'], degrees)

        # change circles position
        for circle in self.circles:
            circle['center']=_rotatePoint(circle['center'], degrees)
            circle['end']=_rotatePoint(circle['end'], degrees)

        # change arcs position
        for arc in self.arcs:
            arc['start']=_rotatePoint(arc['start'], degrees)
            arc['end']=_rotatePoint(arc['end'], degrees)

        # change pads positions
        for pad in self.pads:
            pad['pos']=_rotatePoint(pad['pos'], degrees)

        # change models
        for model in self.models:
            model['pos']=_rotatePoint(model['pos'], -degrees)
            model['rotate']['z']=model['rotate']['z']-degrees

    def filterLines(self, layer):
        lines = []
        for line in self.lines:
            if line['layer'] == layer:
                lines.append(line)

        return lines

    def filterCircles(self, layer):
        circles = []
        for circle in self.circles:
            if circle['layer'] == layer:
                circles.append(circle)

        return circles

    def filterArcs(self, layer):
        arcs = []
        for arc in self.arcs:
            if arc['layer'] == layer:
                arcs.append(arc)

        return arcs

    # Return the geometric bounds for a given layer
    # Includes lines, arcs, circles
    def geometricBoundingBox(self, layer):

        bb = BoundingBox()

        # Add all lines
        lines = self.filterLines(layer)
        for l in lines:
            bb.addPoint(l['start']['x'], l['start']['y'])
            bb.addPoint(l['end']['x'], l['end']['y'])

        # Add all circles
        circles=self.filterCircles(layer)
        for c in circles:
            cx = c['center']['x']
            cy = c['center']['y']
            ex = c['end']['x']
            ey = c['end']['y']

            dx = ex - cx
            dy = ey - cy

            r = math.sqrt(dx*dx + dy*dy)

            bb.addPoint(cx, cy, radius=r)

        # Add all arcs
        arcs=self.filterArcs(layer)
        for c in arcs:
            cx = c['start']['x']
            cy = c['start']['y']
            ex = c['end']['x']
            ey = c['end']['y']

            dx = ex - cx
            dy = ey - cy

            r = math.sqrt(dx*dx + dy*dy)

            dalpha=1
            alphaend=c['angle']
            if math.fabs(alphaend)<1:
                dalpha=math.fabs(alphaend)/5
            if alphaend<0:
                dalpha=-dalpha
            if math.fabs(alphaend)>0:
                a=0
                c0=[ ex - cx, ey - cy ]
                #print("c0 = ",c0)
                while (alphaend>0 and a<=alphaend) or (alphaend<0 and a>=alphaend):
                    c1=[0,0]
                    c1[0]=math.cos(a/180*3.1415)*c0[0]-math.sin(a/180*3.1415)*c0[1]
                    c1[1]=math.sin(a/180*3.1415)*c0[0]+math.cos(a/180*3.1415)*c0[1]

                    bb.addPoint(cx + c1[0], cy + c1[1])
                    a=a+dalpha

            bb.addPoint(ex, None)

        return bb


    def filterGraphs(self, layer):
        return (self.filterLines(layer) +
                self.filterCircles(layer) +
                self.filterArcs(layer))

    def getPadsByNumber(self, pad_number):
        pads = []
        for pad in self.pads:
            if str(pad['number']).upper() == str(pad_number).upper():
                pads.append(pad)

        return pads

    def filterPads(self, pad_type):
        pads = []
        for pad in self.pads:
            if pad['type'] == pad_type:
                pads.append(pad)

        pads = sorted(pads, key = lambda p : str(p['number']))

        return pads

    # Get the middle position between pads
    # Use the outer dimensions of pads to handle footprints with pads of different sizes
    def padMiddlePosition(self, pads=None):

        bb = self.overpadsBounds(pads)
        return bb.center

    def padsBounds(self, pads=None):

        bb = BoundingBox()

        if pads == None:
            pads = self.pads

        for pad in pads:
            pos = pad['pos']
            bb.addPoint(pos['x'], pos['y'])

        return bb

    def overpadsBounds(self, pads=None):

        bb = BoundingBox()

        if pads == None:
            pads = self.pads

        for pad in pads:
            pos = pad['pos']
            px = pos['x']
            py = pos['y']

            # Pad outer dimensions
            sx = pad['size']['x']
            sy = pad['size']['y']

            angle = -pad['pos']['orientation']

            # Add each "corner" of the pad (even for oval shapes)

            p1 = _rotatePoint({'x': -sx/2, 'y': -sy/2}, angle)
            p2 = _rotatePoint({'x': -sx/2, 'y': +sy/2}, angle)
            p3 = _rotatePoint({'x': +sx/2, 'y': +sy/2}, angle)
            p4 = _rotatePoint({'x': +sx/2, 'y': -sy/2}, angle)

            points = [p1, p2, p3, p4]

            # Add more points for custom pad shapes
            if pad['shape'] == 'custom':
                for p in pad['primitives']:
                    if p['type'] == 'gr_poly':
                        # Add polygon points
                        for point in p['pts']:
                            points.append(_rotatePoint(point, angle))
                    elif p['type'] == 'gr_line':
                        # Add line points
                        s = _rotatePoint(p['start'], angle)
                        e = _rotatePoint(p['end'], angle)
                        w = p['width']
                        points.append(_movePoint(s, {'x': -w/2, 'y': -w/2}))
                        points.append(_movePoint(s, {'x': -w/2, 'y': +w/2}))
                        points.append(_movePoint(s, {'x': +w/2, 'y': +w/2}))
                        points.append(_movePoint(s, {'x': +w/2, 'y': -w/2}))
                        points.append(_movePoint(e, {'x': -w/2, 'y': -w/2}))
                        points.append(_movePoint(e, {'x': -w/2, 'y': +w/2}))
                        points.append(_movePoint(e, {'x': +w/2, 'y': +w/2}))
                        points.append(_movePoint(e, {'x': +w/2, 'y': -w/2}))
                    elif p['type'] == 'gr_arc':
                        # Add arc points
                        # TODO
                        pass
                    elif p['type'] == 'gr_circle':
                        # Add circle points
                        c = _rotatePoint(p['center'], angle)
                        e = _rotatePoint(p['end'], angle)
                        r = math.sqrt((e['x']-c['x'])**2 + (e['y']-c['y'])**2)
                        w = p['width']
                        points.append(_movePoint(c, {'x': -r-w/2, 'y': 0}))
                        points.append(_movePoint(c, {'x': +r+w/2, 'y': 0}))
                        points.append(_movePoint(c, {'x': 0, 'y': -r-w/2}))
                        points.append(_movePoint(c, {'x': 0, 'y': +r+w/2}))

            for p in points:
                x = px + p['x']
                y = py + p['y']
                bb.addPoint(x,y)

        return bb

    def _formatText(self, text_type, text, se):

        """
        Text is formatted like thus:
        (fp_text <type> <value> (at <x> <y> <R>*) (layer <layer>)
          (effects (font (size <sx> <sy>) (thickness <t>)))
        )
        """

        # Text
        se.startGroup('fp_text')

        # Extract position informat
        tp = text['pos']
        pos = [tp['x'], tp['y']]
        rot = tp.get('orientation',0)
        if not rot in [0, None]:
            pos.append(rot)

        se.addItems([text_type, text[text_type], {'at': pos}, {'layer': text['layer']}], newline=False)

        tf = text['font']

        font = [{'font': [{'size': [tf['height'], tf['width']]}, {'thickness': tf['thickness']}]}]
        italic = tf.get('italic',None)
        if italic:
            font.append(italic)

        se.startGroup('effects', indent=True)
        se.addItems(font, newline=False)
        se.endGroup(False)
        se.endGroup(True)

    def _formatLine(self, line, se):
        se.startGroup('fp_line', newline=True, indent=False)

        start = line['start']
        end = line['end']

        fp_line = [
            {'start': [start['x'], start['y']]},
            {'end': [end['x'], end['y']]},
            {'layer': line['layer']},
            {'width': line['width']}
            ]

        se.addItems(fp_line, newline=False)
        se.endGroup(newline=False)

    def _formatCircle(self, circle, se):
        se.startGroup('fp_circle', newline=True, indent=False)

        center = circle['center']
        end = circle['end']

        fp_circle = [
            {'center': [center['x'], center['y']]},
            {'end': [end['x'], end['y']]},
            {'layer': circle['layer']},
            {'width': circle['width']}
            ]

        se.addItems(fp_circle, newline=False)
        se.endGroup(newline=False)

    def _formatArc(self, arc, se):
        se.startGroup('fp_arc', newline=True, indent=False)

        start = arc['start']
        end = arc['end']

        fp_arc = [
            {'start': [start['x'], start['y']]},
            {'end': [end['x'], end['y']]},
            {'angle': arc['angle']},
            {'layer': arc['layer']},
            {'width': arc['width']}
            ]

        se.addItems(fp_arc, newline=False)
        se.endGroup(newline=False)

    def _formatPad(self, pad, se):
        pos = pad['pos']

        se.startGroup('pad', newline=True, indent=False)

        fp_pad = [pad['number'], pad['type'], pad['shape']]

        at = [pos['x'], pos['y']]

        rot = pos.get('orientation',0)
        if rot:
            at.append(rot)

        fp_pad.append({'at': at})

        fp_pad.append({'size': [pad['size']['x'], pad['size']['y']]})

        # Drill?
        _drill = pad.get('drill', None)

        if _drill:
            d = []
            if _drill['shape'] == 'oval':
                d.append('oval')

            if _drill['size']:
                d.append(_drill['size']['x'])

                # Oval drill requires x,y pair
                if _drill['shape'] == 'oval':
                    d.append(_drill['size']['y'])

            if _drill['offset']:
                o = [_drill['offset']['x'], _drill['offset']['y']]
                d.append({'offset': o})

            fp_pad.append({'drill': d})

        # Layers
        fp_pad.append({'layers': pad['layers']})

        se.addItems(fp_pad, newline=False)

        extras = []

        # die length
        if pad['die_length']:
            extras.append({'die_length': pad['die_length']})

        # rect_delta
        if pad['rect_delta']:
            extras.append({'rect_delta': pad['rect_delta']})

        ## clearances zones settings
        # clearance
        if pad['clearance']:
            extras.append({'clearance': pad['clearance']})
        # solder mask margin
        if pad['solder_mask_margin']:
            extras.append({'solder_mask_margin': pad['solder_mask_margin']})
        # solder paste margin
        if pad['solder_paste_margin']:
            extras.append({'solder_paste_margin': pad['solder_paste_margin']})
        # solder paste margin ratio
        if pad['solder_paste_margin_ratio']:
            extras.append({'solder_paste_margin_ratio': pad['solder_paste_margin_ratio']})

        ## copper zones settings
        # zone connect
        if pad['zone_connect']:
            extras.append({'zone_connect': pad['zone_connect']})
        # thermal width
        if pad['thermal_width']:
            extras.append({'thermal_width': pad['thermal_width']})
        # thermal gap
        if pad['thermal_gap']:
            extras.append({'thermal_gap': pad['thermal_gap']})

        # TODO: properly format custom pad shapes

        if len(extras) > 0:
            se.addItems(extras, newline=True, indent=True)
            se.unIndent()

        se.endGroup(newline=False)

    def _formatModel(self, model, se):
        se.startGroup('model', newline=True, indent=False)

        se.addItems(model['file'],newline=False)

        """
          at
          scale
          rotate
        """

        at = model['pos']
        sc = model['scale']
        ro = model['rotate']

        se.addItems({'at': {'xyz': [at['x'],at['y'],at['z']]}}, newline=True, indent=True)
        se.addItems({'scale': {'xyz': [sc['x'],sc['y'],sc['z']]}}, newline=True, indent=False)
        se.addItems({'rotate': {'xyz': [ro['x'],ro['y'],ro['z']]}}, newline=True)

        se.endGroup(newline=True)

    def save(self, filename=None):
        if not filename:
            filename = self.filename

        se = sexpr.SexprBuilder('module')

        # Hex value of current epoch timestamp (in seconds)
        tedit = hex(int(time.time())).upper()[2:]

        # Output must be precisely formatted

        """ Header order is as follows
        (*items are optional)

        module <name> locked* <layer>  <tedit>
        descr
        tags
        autoplace_cost_90*
        autoplace_cost_180*
        solder_mask_margin*
        solder_paste_margin*
        solder_paste_ratio*
        clearance*
        attr

        fp_text reference
        fp_text value
        [fp_text user]
        """

        # Build the header string
        header = [self.name]
        if self.locked:
            header.append('locked')
        header.append({'layer': self.layer})
        header.append({'tedit': tedit})

        se.addItems(header, newline=False)
        se.addItems({'descr': self.description}, indent=True)
        se.addItems({'tags': self.tags})


        # Following items are optional (only written if non-zero)
        se.addOptItem('autoplace_cost90', self.autoplace_cost90)
        se.addOptItem('autoplace_cost180', self.autoplace_cost180)
        se.addOptItem('solder_mask_margin', self.solder_mask_margin)
        se.addOptItem('solder_paste_margin', self.solder_paste_margin)
        se.addOptItem('solder_paste_ratio', self.solder_paste_ratio)
        se.addOptItem('clearance', self.clearance)

        # 'pth' type is assumed
        attr = self.attribute.lower()
        if attr in ['smd', 'virtual']:
            se.addItems({'attr': attr})

        # Add text items
        self._formatText('reference', self.reference, se)
        self._formatText('value', self.value, se)

        for text in self.userText:
            self._formatText('user', text, se)

        # Add Line Data
        for line in self.lines:
            self._formatLine(line, se)

        # Add Circle Data
        for circle in self.circles:
            self._formatCircle(circle, se)

        # Add Arc Data
        for arc in self.arcs:
            self._formatArc(arc, se)

        # Add Pad Data
        for pad in self.pads:
            self._formatPad(pad, se)

        # Add Model Data
        for model in self.models:
            self._formatModel(model, se)

        se.endGroup(True)

        with open(filename, 'w', newline='\n') as f:
            f.write(se.output)
            f.write('\n')

if __name__ == '__main__':
    pass
