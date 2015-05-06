#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sexpr

class KicadMod(object):
    """
    A class to parse kicad_mod files format of the KiCad
    """
    def __init__(self, filename):
        self.filename = filename

        # read the s-expression data
        f = open(filename)
        sexpr_data = ''.join(f.readlines())
        sexpr_data = sexpr.parse_sexp(sexpr_data)
        self.sexpr_data = sexpr_data

        # module name
        self.name = self.sexpr_data[1]

        # locked flag
        self.locked = True if self._hasValue(self.sexpr_data, 'locked') else False

        # description
        self.description = self._getValue('descr')

        # tags
        self.tags = self._getValue('tags')

        # attribute
        self.attribute =  self._getValue('attr')
        if not self.attribute: self.attribute = 'pth'

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

    def _hasValue(self, data, value):
        for i in data:
            if type(i) == type([]):
                if self._hasValue(i, value):
                    return True
            elif str(i) == value:
                return True
        return False

    def _getArray(self, data, value, result=None):
        if result is None: result = []
        for i in data:
            if type(i) == type([]):
                self._getArray(i, value, result)
            else:
                if i == value:
                    result.append(data)
        return result

    def _createArray(self, new_array, place_after=None):
        # check first if array already exists
        array = self._getArray(self.sexpr_data, new_array[0])
        if array:
            index = self.sexpr_data.index(array[0])
            self.sexpr_data.pop(index)
            self.sexpr_data.insert(index, new_array)
            return

        # place_after must be an array with desired position
        # the new array will be placed after the first matched position
        for field in place_after:
            pos_array = self._getArray(self.sexpr_data, field)
            if pos_array:
                self.sexpr_data.insert(self.sexpr_data.index(pos_array[0]) + 1, new_array)
                break

    def _unlock(self):
        try:
            self.sexpr_data.remove('locked')
        except ValueError:
            pass

    def _lock(self):
        self.unlock()
        self.sexpr_data.insert(2, 'locked')

    def _getValue(self, field):
        a = self._getArray(self.sexpr_data, field)
        return None if not a else a[0][1]

    def _getText(self, which_text):
        which_text = which_text.lower()
        assert which_text in ['reference', 'value', 'user'], "which_text must be one of the following options: 'reference', 'value', 'user'"
        result = []
        for text in self._getArray(self.sexpr_data, 'fp_text'):
            if text[1] == which_text:
                text_dict = {}
                text_dict[which_text] = text[2]

                # text position
                a = self._getArray(text, 'at')[0]
                text_dict['pos'] = {'x':a[1], 'y':a[2]}
                if len(a) > 3: text_dict['pos']['orientation'] = a[3]

                # text layer
                a = self._getArray(text, 'layer')[0]
                text_dict['layer'] = a[1]

                # text font
                a = self._getArray(text, 'font')[0]
                text_dict['font'] = {'height':a[1][1], 'width':a[1][2], 'thickness':a[2][1]}
                text_dict['font']['italic'] = self._hasValue(a, 'italic')

                # text hide
                text_dict['hide'] = self._hasValue(text, 'italic')

                result.append(text_dict)

        return result

    def _getLines(self, layer=None):
        lines = []
        for line in self._getArray(self.sexpr_data, 'fp_line'):
            line_dict = {}
            if self._hasValue(line, layer) or layer == None:
                a = self._getArray(line, 'start')[0]
                line_dict['start'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(line, 'end')[0]
                line_dict['end'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(line, 'layer')[0]
                line_dict['layer'] = a[1]

                a = self._getArray(line, 'width')[0]
                line_dict['width'] = a[1]

                lines.append(line_dict)

        return lines

    def _getCircles(self, layer=None):
        circles = []
        for circle in self._getArray(self.sexpr_data, 'fp_circle'):
            circle_dict = {}
            if self._hasValue(circle, layer) or layer == None:
                a = self._getArray(circle, 'center')[0]
                circle_dict['center'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(circle, 'end')[0]
                circle_dict['end'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(circle, 'layer')[0]
                circle_dict['layer'] = a[1]

                a = self._getArray(circle, 'width')[0]
                circle_dict['width'] = a[1]

                circles.append(circle_dict)

        return circles

    def _getArcs(self, layer=None):
        arcs = []
        for arc in self._getArray(self.sexpr_data, 'fp_arc'):
            arc_dict = {}
            if self._hasValue(arc, layer) or layer == None:
                a = self._getArray(arc, 'start')[0]
                arc_dict['start'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(arc, 'end')[0]
                arc_dict['end'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(arc, 'angle')[0]
                arc_dict['angle'] = a[1]

                a = self._getArray(arc, 'layer')[0]
                arc_dict['layer'] = a[1]

                a = self._getArray(arc, 'width')[0]
                arc_dict['width'] = a[1]

                arcs.append(arc_dict)

        return arcs

    def _getPads(self):
        pads = []
        for pad in self._getArray(self.sexpr_data, 'pad'):
            pad_dict = {'number':pad[1], 'type':pad[2], 'shape':pad[3]}

            a = self._getArray(pad, 'at')[0]
            pad_dict['pos'] = {'x':[1], 'y':[2]}
            if len(a) > 3: pad_dict['pos']['orientation'] = a[3]

            a = self._getArray(pad, 'size')[0]
            pad_dict['size'] = {'x':[1], 'y':[2]}

            a = self._getArray(pad, 'layers')[0]
            pad_dict['layers'] = a[1:]

            # drill
            drill = self._getArray(pad, 'drill')
            if drill:
                drill = drill[0]
                pad_dict['drill'] = {}

                # offset
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
                if len(drill) > 1:
                    x = drill[1]
                    y = drill[2] if len(drill) > 2 else x
                    pad_dict['drill']['size'] = {'x':x, 'y':y}

            a = self._getArray(pad, 'die_length')
            if a: pad_dict['die_length'] = a[0][1]

            a = self._getArray(pad, 'rect_delta')
            if a: pad_dict['rect_delta'] = a[0][1:]

            pads.append(pad_dict)

        return pads

    def _getModels(self):
        models_array = self._getArray(self.sexpr_data, 'model')

        models = []
        for model in models_array:
            model_dict = {'file':model[1]}

            # position
            xyz = self._getArray(self._getArray(model, 'at'), 'xyz')[0]
            model_dict['pos'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            # scale
            xyz = self._getArray(self._getArray(model, 'scale'), 'xyz')[0]
            model_dict['scale'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            # rotate
            xyz = self._getArray(self._getArray(model, 'rotate'), 'xyz')[0]
            model_dict['rotate'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            models.append(model_dict)

        return models

if __name__ == '__main__':
    module = KicadMod('/tmp/SOT-23.kicad_mod')
    module = KicadMod('/tmp/USB_A_Vertical.kicad_mod')

    print('--- module.name')
    print(module.name)
    print('--- module.description')
    print(module.description)
    print('--- module.tags')
    print(module.tags)
    print('--- module.attribute')
    print(module.attribute)
    print('--- module.reference')
    print(module.reference)
    print('--- module.value')
    print(module.value)
    print('--- module.userText')
    print(module.userText)
    print('--- module.lines')
    print(module.lines)
    print('--- module.circles')
    print(module.circles)
    print('--- module.arcs')
    print(module.arcs)
    print('--- module.pads')
    print(module.pads)
    print('--- module.models')
    print(module.models)
