# -*- coding: utf-8 -*-

import sys, shlex

class Description(object):
    """
    A class to parse description information of Schematic Files Format of the KiCad
    TODO: Need to be done, currently just stores the raw data read from file
    """
    def __init__(self, data):
        self.raw_data = data

class Component(object):
    """
    A class to parse components of Schematic Files Format of the KiCad
    """
    _L_KEYS = ['name', 'ref']
    _U_KEYS = ['unit', 'convert', 'time_stamp']
    _P_KEYS = ['posx', 'posy']
    _AR_KEYS = ['path', 'ref', 'part']
    _F_KEYS = ['id', 'ref', 'orient', 'posx', 'posy', 'size', 'attributs', 'hjust', 'props', 'name']

    _KEYS = {'L':_L_KEYS, 'U':_U_KEYS, 'P':_P_KEYS, 'AR':_AR_KEYS, 'F':_F_KEYS}
    def __init__(self, data):
        self.labels = {}
        self.unit = {}
        self.position = {}
        self.references = []
        self.fields = []
        self.old_stuff = []

        for line in data:
            if line[0] == '\t':
                self.old_stuff.append(line)
                continue

            line = line.replace('\n', '')
            s = shlex.shlex(line)
            s.whitespace_split = True
            s.commenters = ''
            s.quotes = '"'
            line = list(s)

            # select the keys list and default values array
            if line[0] in self._KEYS:
                key_list = self._KEYS[line[0]]
                values = line[1:] + ['' for n in range(len(key_list) - len(line[1:]))]

            if line[0] == 'L':
                self.labels = dict(zip(key_list,values))
            elif line[0] == 'U':
                self.unit = dict(zip(key_list,values))
            elif line[0] == 'P':
                self.position = dict(zip(key_list,values))
            elif line[0] == 'AR':
                self.references.append(dict(zip(key_list,values)))
            elif line[0] == 'F':
                self.fields.append(dict(zip(key_list,values)))

    # TODO: error checking
    # * check if field_data is a dictionary
    # * check if at least 'ref' and 'name' were passed
    # * ignore invalid items of field_data on merging
    # TODO: enhancements
    # * 'value' could be used instead of 'ref'
    def addField(self, field_data):
        def_field = {'id':None, 'ref':None, 'orient':'H', 'posx':'0', 'posy':'0', 'size':'50',
                     'attributs':'0001', 'hjust':'C', 'props':'CNN', 'name':'~'}

        # merge dictionaries and set the id value
        field = dict(list(def_field.items()) + list(field_data.items()))
        field['id'] = str(len(self.fields))

        self.fields.append(field)
        return field

class Sheet(object):
    """
    A class to parse sheets of Schematic Files Format of the KiCad
    """
    _S_KEYS = ['topLeftPosx', 'topLeftPosy','botRightPosx', 'botRightPosy']
    _U_KEYS = ['uniqID']
    _F_KEYS = ['id', 'value', 'IOState', 'side', 'posx', 'posy', 'size']

    _KEYS = {'S':_S_KEYS, 'U':_U_KEYS, 'F':_F_KEYS}
    def __init__(self, data):
        self.shape = {}
        self.unit = {}
        self.fields = []
        for line in data:
            line = line.replace('\n', '')
            s = shlex.shlex(line)
            s.whitespace_split = True
            s.commenters = ''
            s.quotes = '"'
            line = list(s)
            # select the keys list and default values array
            if line[0] in self._KEYS:
                key_list = self._KEYS[line[0]]
                values = line[1:] + ['' for n in range(len(key_list) - len(line[1:]))]
            if line[0] == 'S':
                self.shape = dict(zip(key_list,values))
            elif line[0] == 'U':
                self.unit = dict(zip(key_list,values))
            elif line[0][0] == 'F':
                key_list = self._F_KEYS
                values = line + ['' for n in range(len(key_list) - len(line))]
                self.fields.append(dict(zip(key_list,values)))

class Bitmap(object):
    """
    A class to parse bitmaps of Schematic Files Format of the KiCad
    TODO: Need to be done, currently just stores the raw data read from file
    """
    def __init__(self, data):
        self.raw_data = data

class Schematic(object):
    """
    A class to parse Schematic Files Format of the KiCad
    """
    def __init__(self, filename):
        f = open(filename)
        self.filename = filename
        self.header = f.readline()
        self.libs = []
        self.eelayer = None
        self.description = None
        self.components = []
        self.sheets = []
        self.bitmaps = []
        self.texts = []
        self.wires = []
        self.entries = []
        self.conns = []
        self.noconns = []

        if not 'EESchema Schematic File' in self.header:
            self.header = None
            sys.stderr.write('The file is not a KiCad Schematic File\n')
            return

        building_block = False

        while True:
            line = f.readline()
            if not line: break

            if line.startswith('LIBS:'):
                self.libs.append(line)

            elif line.startswith('EELAYER END'):
                pass
            elif line.startswith('EELAYER'):
                self.eelayer = line

            elif not building_block:
                if line.startswith('$'):
                    building_block = True
                    block_data = []
                    block_data.append(line)
                elif line.startswith('Text'):
                    data = {'desc':line, 'data':f.readline()}
                    self.texts.append(data)
                elif line.startswith('Wire'):
                    data = {'desc':line, 'data':f.readline()}
                    self.wires.append(data)
                elif line.startswith('Entry'):
                    data = {'desc':line, 'data':f.readline()}
                    self.entries.append(data)
                elif line.startswith('Connection'):
                    data = {'desc':line}
                    self.conns.append(data)
                elif line.startswith('NoConn'):
                    data = {'desc':line}
                    self.noconns.append(data)

            elif building_block:
                block_data.append(line)
                if line.startswith('$End'):
                    building_block = False

                    if line.startswith('$EndDescr'):
                        self.description = Description(block_data)
                    if line.startswith('$EndComp'):
                        self.components.append(Component(block_data))
                    if line.startswith('$EndSheet'):
                        self.sheets.append(Sheet(block_data))
                    if line.startswith('$EndBitmap'):
                        self.bitmaps.append(Bitmap(block_data))

    def save(self, filename=None):
        # check whether it has header, what means that sch file was loaded fine
        if not self.header: return

        if not filename: filename = self.filename

        # insert the header
        to_write = []
        to_write += [self.header]

        # LIBS
        to_write += self.libs

        # EELAYER
        to_write += [self.eelayer, 'EELAYER END\n']

        # Description
        to_write += self.description.raw_data

        # Sheets
        for sheet in self.sheets:
            to_write += ['$Sheet\n']
            if sheet.shape:
                line = 'S '
                for key in sheet._S_KEYS:
                    line+= sheet.shape[key] + ' '
                to_write += [line.rstrip() + '\n']
            if sheet.unit:
                line = 'U '
                for key in sheet._U_KEYS:
                    line += sheet.unit[key] + ' '
                to_write += [line.rstrip() + '\n']

            for field in sheet.fields:
                line = ''
                for key in sheet._F_KEYS:
                    line += field[key] + ' '
                to_write += [line.rstrip() + '\n']
            to_write += ['$EndSheet\n']

        # Components
        for component in self.components:
            to_write += ['$Comp\n']
            if component.labels:
                line = 'L '
                for key in component._L_KEYS:
                    line += component.labels[key] + ' '
                to_write += [line.rstrip() + '\n']

            if component.unit:
                line = 'U '
                for key in component._U_KEYS:
                    line += component.unit[key] + ' '
                to_write += [line.rstrip() + '\n']

            if component.position:
                line = 'P '
                for key in component._P_KEYS:
                    line += component.position[key] + ' '
                to_write += [line.rstrip() + '\n']

            for reference in component.references:
                if component.references:
                    line = 'AR '
                    for key in component._AR_KEYS:
                        line += reference[key] + ' '
                    to_write += [line.rstrip() + '\n']

            for field in component.fields:
                line = 'F '
                for key in component._F_KEYS:
                    line += field[key] + ' '
                to_write += [line.rstrip() + '\n']

            if component.old_stuff:
                to_write += component.old_stuff

            to_write += ['$EndComp\n']

        # Bitmaps
        for bitmap in self.bitmaps:
            to_write += bitmap.raw_data

        # Texts
        for text in self.texts:
            to_write += [text['desc'], text['data']]

        # Wires
        for wire in self.wires:
            to_write += [wire['desc'], wire['data']]

        # Entries
        for entry in self.entries:
            to_write += [entry['desc'], entry['data']]

        # Connections
        for conn in self.conns:
            to_write += [conn['desc']]

        # No Connetions
        for noconn in self.noconns:
            to_write += [noconn['desc']]

        to_write += ['$EndSCHEMATC\n']

        f = open(filename, 'w')
        f.writelines(to_write)
