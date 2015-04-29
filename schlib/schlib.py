# -*- coding: utf-8 -*-

import sys, shlex
import os.path

class Component(object):
    """
    A class to parse components of Schematic Libraries Files Format of the KiCad
    """

    _DEF_KEYS = ['name','reference','unused','text_offset','draw_pinnumber','draw_pinname','unit_count','units_locked','option_flag']
    _F0_KEYS = ['reference','posx','posy','text_size','text_orient','visibility','htext_justify','vtext_justify']
    _FN_KEYS = ['name','posx','posy','text_size','text_orient','visibility','htext_justify','vtext_justify']
    _ARC_KEYS = ['posx','posy','radius','start_angle','end_angle','unit','convert','thickness','fill','startx','starty','endx','endy']
    _CIRCLE_KEYS = ['posx','posy','radius','unit','convert','thickness','fill']
    _POLY_KEYS = ['point_count','unit','convert','thickness','points','fill']
    _RECT_KEYS = ['startx','starty','endx','endy','unit','convert','thickness','fill']
    _TEXT_KEYS = ['direction','posx','posy','text_size','text_type','unit','convert','text', 'italic', 'bold', 'hjustify', 'vjustify']
    _PIN_KEYS = ['name','num','posx','posy','length','direction','name_text_size','num_text_size','unit','convert','electrical_type','pin_type']

    _DRAW_KEYS = {'arcs':_ARC_KEYS, 'circles':_CIRCLE_KEYS, 'polylines':_POLY_KEYS, 'rectangles':_RECT_KEYS, 'texts':_TEXT_KEYS, 'pins':_PIN_KEYS}
    _DRAW_ELEMS = {'arcs':'A', 'circles':'C', 'polylines':'P', 'rectangles':'S', 'texts':'T', 'pins':'X'}

    _KEYS = {'DEF':_DEF_KEYS, 'F0':_F0_KEYS, 'F1':_FN_KEYS, 'F2':_FN_KEYS, 'F3':_FN_KEYS, 'F4':_FN_KEYS,
             'A':_ARC_KEYS, 'C':_CIRCLE_KEYS, 'P':_POLY_KEYS, 'S':_RECT_KEYS, 'T':_TEXT_KEYS, 'X':_PIN_KEYS}

    def __init__(self, data, comments):
        self.comments = comments
        self.fplist = []
        self.aliases = []
        building_fplist = False
        building_draw = False
        for line in data:
            line = line.replace('\n', '')
            s = shlex.shlex(line)
            s.whitespace_split = True
            s.commenters = ''
            s.quotes = '"'
            line = list(s)

            if line[0] in self._KEYS:
                key_list = self._KEYS[line[0]]
                values = line[1:] + ['' for n in range(len(key_list) - len(line[1:]))]

            if line[0] == 'DEF':
                self.definition = dict(zip(self._DEF_KEYS,values))

            elif line[0] == 'F0':
                self.fields = []
                self.fields.append(dict(zip(self._F0_KEYS,values)))

            elif line[0][0] == 'F':
                self.fields.append(dict(zip(self._FN_KEYS,values)))

            elif line[0] == 'ALIAS':
                self.aliases = [alias for alias in line[1:]]

            elif line[0] == '$FPLIST':
                building_fplist = True
                self.fplist = []

            elif line[0] == '$ENDFPLIST':
                building_fplist = False

            elif line[0] == 'DRAW':
                building_draw = True
                self.draw = {
                    'arcs':[],
                    'circles':[],
                    'polylines':[],
                    'rectangles':[],
                    'texts':[],
                    'pins':[]
                }

            elif line[0] == 'ENDDRAW':
                building_draw = False

            else:
                if building_fplist:
                    self.fplist.append(line[0])

                elif building_draw:
                    if line[0] == 'A':
                        self.draw['arcs'].append(dict(zip(self._ARC_KEYS,values)))
                    if line[0] == 'C':
                        self.draw['circles'].append(dict(zip(self._CIRCLE_KEYS,values)))
                    if line[0] == 'P':
                        n_points = int(line[1])
                        points = line[5:5+(2*n_points)]
                        values = line[1:5] + [points]
                        if len(line) > (5 + len(points)):
                            values += [line[-1]]
                        else:
                            values += ['']
                        self.draw['polylines'].append(dict(zip(self._POLY_KEYS,values)))
                    if line[0] == 'S':
                        self.draw['rectangles'].append(dict(zip(self._RECT_KEYS,values)))
                    if line[0] == 'T':
                        self.draw['texts'].append(dict(zip(self._TEXT_KEYS,values)))
                    if line[0] == 'X':
                        self.draw['pins'].append(dict(zip(self._PIN_KEYS,values)))

        # define some shortcuts
        self.name = self.definition['name']
        self.reference = self.definition['reference']
        self.pins = self.draw['pins']

    def getPinsByName(self, name):
        pins = []
        for pin in self.pins:
            if pin['name'] == name:
                pins.append(pin)

        return pins

    def getPinByNumber(self, num):
        for pin in self.draw['pins']:
            if pin['num'] == str(num):
                return pin

        return None

    def filterPins(self, name=None, direction=None, electrical_type=None):
        pins = []

        for pin in self.pins:
            if ((name and pin['name'] == name) or
                (direction and pin['direction'] == direction) or
                (electrical_type and pin['electrical_type'] == electrical_type)):
                pins.append(pin)

        return pins

class SchLib(object):
    """
    A class to parse Schematic Libraries Files Format of the KiCad
    """
    def __init__(self, filename, create=False):
        self.filename = filename
        self.header = []
        self.components = []

        if create:
            if not os.path.isfile(filename):
                f = open(filename, 'w')
                self.header = ['EESchema-LIBRARY Version 2.3\n', '#encoding utf-8\n']
                return

        f = open(filename)
        self.header = [f.readline()]

        if self.header and not 'EESchema-LIBRARY' in self.header[0]:
            self.header = None
            sys.stderr.write('The file is not a KiCad Schematic Library File\n')
            return

        self.header.append(f.readline())
        building_component = False

        comments = []
        for i, line in enumerate(f.readlines()):
            if line.startswith('#'):
                comments.append(line)

            elif line.startswith('DEF'):
                building_component = True
                component_data = []
                component_data.append(line)

            elif building_component:
                component_data.append(line)
                if line.startswith('ENDDEF'):
                    building_component = False
                    self.components.append(Component(component_data, comments))
                    comments = []

    def getComponentByName(self, name):
        for component in self.components:
            if component.definition['name'] == name:
                return component

        return None

    def save(self, filename=None):
        # check whether it has header, what means that schlib file was loaded fine
        if not self.header: return

        if not filename: filename = self.filename

        # insert the header
        to_write = self.header

        # insert the components
        for component in self.components:
            # append the component comments
            to_write += component.comments

            # DEF
            line = 'DEF '
            for key in Component._DEF_KEYS:
                line += component.definition[key] + ' '

            line = line.rstrip() + '\n'
            to_write.append(line)

            # FIELDS
            line = 'F'
            for i, f in enumerate(component.fields):
                line = 'F' + str(i) + ' '

                if i == 0:
                    keys_list = Component._F0_KEYS
                else:
                    keys_list = Component._FN_KEYS

                for key in keys_list:
                    line += component.fields[i][key] + ' '

                line = line.rstrip() + '\n'
                to_write.append(line)

            # ALIAS
            if len(component.aliases) > 0:
                line = 'ALIAS '
                for alias in component.aliases:
                    line += alias + ' '

                line = line.rstrip() + '\n'
                to_write.append(line)

            # $FPLIST
            if len(component.fplist) > 0:
                to_write.append('$FPLIST\n')
                for fp in component.fplist:
                    to_write.append(' ' + fp + '\n')

            # $ENDFPLIST
                to_write.append('$ENDFPLIST\n')

            # DRAW
            to_write.append('DRAW\n')
            for elem in component.draw.items():
                for item in component.draw[elem[0]]:
                    keys_list = Component._DRAW_KEYS[elem[0]]
                    line = Component._DRAW_ELEMS[elem[0]] + ' '
                    for k in keys_list:
                        if k == 'points':
                            for i in item['points']:
                                line += i + ' '
                        else:
                            line += item[k] + ' '

                    line = line.rstrip() + '\n'
                    to_write.append(line)

            # ENDDRAW
            to_write.append('ENDDRAW\n')

            # ENDDEF
            to_write.append('ENDDEF\n')

        # insert the footer
        to_write.append('#\n')
        to_write.append('#End Library\n')

        f = open(filename, 'w')
        f.writelines(to_write)
