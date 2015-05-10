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

    # check if value exists in any element of data
    def _hasValue(self, data, value):
        for i in data:
            if type(i) == type([]):
                if self._hasValue(i, value):
                    return True
            elif str(i) == value:
                return True
        return False

    # return the array which has value as first element
    def _getArray(self, data, value, result=None):
        if result is None: result = []
        for i in data:
            if type(i) == type([]):
                self._getArray(i, value, result)
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
        # place_after must be an array with the desired position
        # the new array will be placed after the last matched position
        for field in place_after:
            pos_array = self._getArray(self.sexpr_data, field)
            if pos_array:
                self.sexpr_data.insert(self.sexpr_data.index(pos_array[len(pos_array)-1]) + 1, new_array)
                break

    # return the second element of the array because the array is expected
    # to have the following format: [key value]
    def _getValue(self, array):
        a = self._getArray(self.sexpr_data, array)
        return None if not a else a[0][1]

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
                a = self._getArray(text, 'font')[0]
                text_dict['font'] = {'height':a[1][1], 'width':a[1][2], 'thickness':a[2][1]}
                text_dict['font']['italic'] = self._hasValue(a, 'italic')

                # text hide
                text_dict['hide'] = self._hasValue(text, 'hide')

                result.append(text_dict)

        return result

    def _addText(self, which_text, data):
        # TODO: should check if all keys of dictionary are valid
        # update the arrays
        for text in data:
            fp_text = ['fp_text', which_text, text[which_text]]

            # text position
            at = ['at', text['pos']['x'], text['pos']['y']]
            if text['pos']['orientation'] != 0: at.append(text['pos']['orientation'])
            fp_text.append(at)

            # layer
            fp_text.append(['layer', text['layer']])

            # text hide
            if text['hide']: fp_text.append(['hide'])

            # effects
            font = ['font', ['size', text['font']['height'], text['font']['width']], ['thickness', text['font']['thickness']]]
            if text['font']['italic']: font.append('italic')
            fp_text.append(['effects', font])

            # create the array
            self._createArray(fp_text, ['fp_text', 'attr', 'tags', 'descr', 'tedit'])


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

    def _addLines(self, lines):
        for line in lines:
            fp_line = ['fp_line',
                ['start', line['start']['x'], line['start']['y']],
                ['end', line['end']['x'], line['end']['y']],
                ['layer', line['layer']],
                ['width', line['width']]]

            self._createArray(fp_line, ['fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])


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

                a = self._getArray(circle, 'layer')[0]
                circle_dict['layer'] = a[1]

                a = self._getArray(circle, 'width')[0]
                circle_dict['width'] = a[1]

                circles.append(circle_dict)

        return circles

    def _addCircles(self, circles):
        for circle in circles:
            fp_circle = ['fp_circle',
                ['center', circle['center']['x'], circle['center']['y']],
                ['end', circle['end']['x'], circle['end']['y']],
                ['layer', circle['layer']],
                ['width', circle['width']]]

            self._createArray(fp_circle, ['fp_circle','fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])

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

                a = self._getArray(arc, 'layer')[0]
                arc_dict['layer'] = a[1]

                a = self._getArray(arc, 'width')[0]
                arc_dict['width'] = a[1]

                arcs.append(arc_dict)

        return arcs

    def _addArcs(self, arcs):
        for arc in arcs:
            fp_arc = ['fp_arc',
                ['start', arc['start']['x'], arc['start']['y']],
                ['end', arc['end']['x'], arc['end']['y']],
                ['angle', arc['angle']],
                ['layer', arc['layer']],
                ['width', arc['width']]]

            self._createArray(fp_arc, ['fp_arc', 'fp_circle','fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])

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

            # rect delta
            pad_dict['rect_delta'] = {}
            a = self._getArray(pad, 'rect_delta')
            if a: pad_dict['rect_delta'] = a[0][1:]

            pads.append(pad_dict)

        return pads

    def _addPads(self, pads):
        for p in pads:
            # number, type, shape
            pad = ['pad', p['number'], p['type'], p['shape']]

            # position
            at = ['at', p['pos']['x'], p['pos']['y']]
            if p['pos']['orientation'] != 0: at.append(p['pos']['orientation'])
            pad.append(at)

            # size
            pad.append(['size', p['size']['x'], p['size']['y']])

            # layers
            pad.append(['layers'] + p['layers'])

            # drill
            if p['drill']:
                drill = ['drill']

                # drill shape
                if p['drill']['shape'] == 'oval':
                    drill += ['oval']

                # drill size
                if p['drill']['size']:
                    drill += [p['drill']['size']['x']]

                    # if shape is oval has y size
                    if p['drill']['shape'] == 'oval':
                        drill += [p['drill']['size']['y']]

                # drill offset
                if p['drill']['offset']:
                    drill += ['offset', p['drill']['offset']['x'], p['drill']['offset']['y']]

                pad.append(drill)

            # die length
            if p['die_length']:
                pad.append(['die_length', p['die_length']])

            # rect_delta
            if p['rect_delta']:
                pad.append(['rect_delta'] + p['rect_delta'])

        self._createArray(pad, ['pad', 'fp_arc', 'fp_circle','fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])


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

    def _addModels(self, models):
        for model in models:
            m = ['model', model['file'],
                ['at', ['xyz', model['pos']['x'], model['pos']['y'], model['pos']['z']]],
                ['scale', ['xyz', model['scale']['x'], model['scale']['y'], model['scale']['z']]],
                ['rotate', ['xyz', model['rotate']['x'], model['rotate']['y'], model['rotate']['z']]]
                ]

            self._createArray(m, ['model', 'pad', 'fp_arc', 'fp_circle','fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])

    def Save(self, filename=None):
        if not filename: filename = self.filename

        # module name
        self.sexpr_data[1] = self.name

        # locked flag
        try:
            self.sexpr_data.remove('locked')
        except ValueError:
            pass
        if self.locked:
            self.sexpr_data.insert(2, 'locked')

        # description
        self._updateCreateArray(['descr', self.description], ['tedit'])

        # tags
        self._updateCreateArray(['descr', self.tags], ['descr', 'tedit'])

        # attribute
        attr = self.attribute.lower()
        assert attr in ['pth', 'smd', 'virtual'], "attribute must be one of the following options: 'pth', 'smd', 'virtual'"
        # when the footprint is PTH the attr isn't explicitly defined, thus the field attr doesn't exists
        try:
            self.sexpr_data.remove(self._getArray(self.sexpr_data, 'attr')[0])
        except IndexError:
            pass
        # create the field attr if not pth
        if attr != 'pth': self._updateCreateArray(['attr', attr], ['tags', 'descr', 'tedit'])

        # remove all existing text arrays
        for text in self._getArray(self.sexpr_data, 'fp_text'):
            self.sexpr_data.remove(text)
        # reference
        self._addText('reference', [self.reference])
        # value
        self._addText('value', [self.value])
        # user text
        self._addText('user', self.userText)

        # lines
        # remove all existing lines arrays
        for line in self._getArray(self.sexpr_data, 'fp_line'):
            self.sexpr_data.remove(line)
        self._addLines(self.lines)

        # circles
        # remove all existing circles arrays
        for circle in self._getArray(self.sexpr_data, 'fp_circle'):
            self.sexpr_data.remove(circle)
        self._addCircles(self.circles)

        # arcs
        # remove all existing arcs arrays
        for arc in self._getArray(self.sexpr_data, 'fp_arc'):
            self.sexpr_data.remove(arc)
        self._addArcs(self.arcs)

        # pads
        # remove all existing pads arrays
        for pad in self._getArray(self.sexpr_data, 'pads'):
            self.sexpr_data.remove(pad)
        self._addPads(self.pads)

        # models
        # remove all existing models arrays
        for model in self._getArray(self.sexpr_data, 'models'):
            self.sexpr_data.remove(model)
        self._addModels(self.models)


if __name__ == '__main__':
    module = KicadMod('/tmp/SOT-23.kicad_mod')
    #module = KicadMod('/tmp/USB_A_Vertical.kicad_mod')

    print('--- module.name')
    print(module.name)
    print('--- module.locked')
    print(module.locked)
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

    print('--- setting data')
    module.name = 'new module name'
    module.locked = False
    module.attribute = 'virtual'
    module.reference['reference'] = 'RES1'
    module.value['value'] = '100K'

    print('--- saving data')
    module.Save()

    print('--- new sexpr data')
    import pprint
    pprint.pprint(module.sexpr_data)
