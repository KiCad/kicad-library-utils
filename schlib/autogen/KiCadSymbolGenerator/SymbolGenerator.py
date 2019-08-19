# KiCadSymbolGenerator ia part of the kicad-library-utils script collection.
# It is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KiCadSymbolGenerator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kicad-library-utils. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2017 by Rene Poeschl

# Library format description
# https://www.compuphase.com/electronics/LibraryFileFormats.pdf

import collections
from enum import Enum
from KiCadSymbolGenerator.DrawingElements import *
from KiCadSymbolGenerator.Point import Point

class AliasConflictError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class uniqueNameManager:
    def __init__(self):
        self.used_names = set()

    def addName(self, name):
        if name in self.used_names:
            raise AliasConflictError('The symbol name {:s} already exists in this lib.'.format(name))
        self.used_names.add(name)

class SymbolField:
    class FieldOrientation(Enum):
        VERTICAL = 'V'
        HORIZONTAL = 'H'

        def __str__(self):
            return self.value

    class FieldVisibility(Enum):
        VISIBLE = 'V'
        INVISIBLE = 'I'

        def __str__(self):
            return self.value

    class FieldAlignment(Enum):
        CENTER = 'C'
        LEFT = 'L'
        RIGHT = 'R'
        TOP = 'T'
        BOTTOM ='B'

        def __str__(self):
            return self.value

    class FieldFontWeight(Enum):
        BOLD = 'B'
        NORMAL = 'N'

        def __str__(self):
            return self.value

    class FieldFontStyle(Enum):
        ITALIC = 'I'
        NORMAL = 'N'

        def __str__(self):
            return self.value

    def __init__(self, **kwargs):
        self.idx = int(kwargs['idx'])
        self.value = str(kwargs['value'])
        self.at = Point(kwargs.get('at'), {})
        self.fontsize = int(kwargs.get('fontsize', 50))

        if self.idx == 0:
            self.name = 'reference'
        elif self.idx == 1:
            self.name = 'value'
        elif self.idx == 2:
            self.name = 'footprint'
        elif self.idx == 3:
            self.name = 'datasheet'
        else:
            self.name = kwargs.get('name', 'F{:d}'.format(self.idx))

        orientation = kwargs.get('orientation', SymbolField.FieldOrientation.HORIZONTAL)
        if isinstance(orientation, SymbolField.FieldOrientation):
            self.orientation = orientation
        else:
            raise TypeError('orientation needs to be of type FieldOrientation')

        visibility = kwargs.get('visibility',
            SymbolField.FieldVisibility.VISIBLE if self.idx < 2 else SymbolField.FieldVisibility.INVISIBLE)
        if isinstance(visibility, SymbolField.FieldVisibility):
            self.visibility = visibility
        else:
            raise TypeError('visibility needs to be of type FieldVisibility')

        alignment_horizontal = kwargs.get('alignment_horizontal', SymbolField.FieldAlignment.CENTER)
        if isinstance(alignment_horizontal, SymbolField.FieldAlignment):
            self.alignment_horizontal = alignment_horizontal
        else:
            raise TypeError('alignment_horizontal needs to be of type FieldAlignment')

        alignment_vertical = kwargs.get('alignment_vertical', SymbolField.FieldAlignment.CENTER)
        if isinstance(alignment_vertical, SymbolField.FieldAlignment):
            self.alignment_vertical = alignment_vertical
        else:
            raise TypeError('alignment_horizontal needs to be of type FieldAlignment')

        fontweight = kwargs.get('fontweight', SymbolField.FieldFontWeight.NORMAL)
        if isinstance(fontweight, SymbolField.FieldFontWeight):
            self.fontweight = fontweight
        else:
            raise TypeError('fontweight needs to be of type FieldFontWeight')

        fontstyle = kwargs.get('fontstyle', SymbolField.FieldFontStyle.NORMAL)
        if isinstance(fontstyle, SymbolField.FieldFontStyle):
            self.fontstyle = fontstyle
        else:
            raise TypeError('fontstyle needs to be of type FieldFontStyle')

    def __str__(self):
        # Fn "value" X Y Size H V C CNN "name"
        # (name only for n >3)
        return 'F{idx:d} "{value:s}" {at:s} {size:d} {orientation:s} {visibility:s} {align_v:s} {align_h:s}{style:s}{weight:s}{name:s}\n'.format(
            name = '' if self.idx < 4 else ' "{name}"'.format(name = self.name),
            idx = self.idx, value = self.value, at = self.at,
            size = self.fontsize, weight = self.fontweight, style = self.fontstyle,
            orientation = self.orientation, visibility = self.visibility,
            align_h = self.alignment_horizontal, align_v = self.alignment_vertical
        )


class DcmEntry:
    def __init__(self, name, **kwargs):
        self.name = name
        self.setDescription(kwargs.get('description'))
        self.setKeywords(kwargs.get('keywords'))
        self.setDatasheet(kwargs.get('datasheet'))

    def setDescription(self, description):
        self.description = str(description)

    def setKeywords(self, keywords):
        self.keywords = str(keywords)

    def setDatasheet(self, datasheet):
        self.datasheet = str(datasheet)

    def __str__(self):
        if self.description is None and self.keywords is None and self.datasheet is None:
            return ''

        dcm_content = '#\n$CMP {:s}\n'.format(self.name)
        if self.description is not None:
            dcm_content += 'D {:s}\n'.format(self.description)
        if self.keywords is not None:
            dcm_content += 'K {:s}\n'.format(self.keywords)
        if self.datasheet is not None:
            dcm_content += 'F {:s}\n'.format(self.datasheet)
        dcm_content += '$ENDCMP\n'

        return dcm_content


class Symbol:
    class PinMarkerVisibility(Enum):
        VISIBLE = 'Y'
        INVISIBLE = 'N'

        def __str__(self):
            return self.value

    class UnitsInterchangable(Enum):
        NOT_INTERCHANGEABLE = 'L'
        INTERCHANGEABLE = 'F'

        def __str__(self):
            return self.value

    class PowerSymbol(Enum):
        POWER_SYMBOL = 'P'
        NORMAL = 'N'

        def __str__(self):
            return self.value

    def __init__(self, symbol_name, used_names_in_lib, **kwargs):
        self.symbol_name = symbol_name
        self.used_names_in_lib = used_names_in_lib
        self.pin_name_offset = int(kwargs.get('offset', 40))
        self.num_units = int(kwargs.get('num_units', 1))
        self.drawing = Drawing()
        self.fields = [None, None,
            SymbolField(idx=2, value=''),
            SymbolField(idx=3, value='')]
        self.lowest_user_field_idx = 4
        self.footprint_filter = []
        self.addFootprintFilter(kwargs.get('footprint_filter', []))
        self.aliases = {}

        dcm_options = kwargs.get('dcm_options', {})
        self.dcm_entry = DcmEntry(name=symbol_name, **dcm_options)

        pin_number_visibility = kwargs.get('pin_number_visibility', Symbol.PinMarkerVisibility.VISIBLE)
        if isinstance(pin_number_visibility, Symbol.PinMarkerVisibility):
            self.pin_number_visibility = pin_number_visibility
        else:
            raise TypeError('pin_number_visibility needs to be of type PinMarkerVisibility')

        pin_name_visibility = kwargs.get('pin_name_visibility', Symbol.PinMarkerVisibility.VISIBLE)
        if isinstance(pin_name_visibility, Symbol.PinMarkerVisibility):
            self.pin_name_visibility = pin_name_visibility
        else:
            raise TypeError('pin_name_visibility needs to be of type PinMarkerVisibility')

        interchangable = kwargs.get('interchangable', Symbol.UnitsInterchangable.INTERCHANGEABLE)
        if isinstance(interchangable, Symbol.UnitsInterchangable):
            self.interchangable = interchangable
        else:
            raise TypeError('interchangable needs to be of type UnitsInterchangable')

        is_power_symbol = kwargs.get('is_power_symbol', Symbol.PowerSymbol.NORMAL)
        if isinstance(is_power_symbol, Symbol.PowerSymbol):
            self.is_power_symbol = is_power_symbol
        else:
            raise TypeError('is_power_symbol needs to be of type PowerSymbol')


    def setReference(self, ref_des, **kwargs):
        self.ref_des = ref_des
        if self.is_power_symbol is Symbol.PowerSymbol.POWER_SYMBOL:
            if not self.ref_des.startswidth('#'):
                self.ref_des = '#' + self.ref_des
            if 'visibility' not in kwargs:
                kwargs['visibility'] = SymbolField.FieldVisibility.INVISIBLE
        self.fields[0] = SymbolField(idx = 0, value = ref_des, **kwargs)

    def setValue(self, **kwargs):
        if 'value' not in kwargs:
            kwargs['value']=self.symbol_name
        self.fields[1] = SymbolField(idx = 1, **kwargs)

    def setDefaultFootprint(self, **kwargs):
        self.fields[2] = SymbolField(idx = 2, **kwargs)

    def setDescriptionField(self, **kwargs):
        self.fields[3] = SymbolField(idx = 3, **kwargs)

    def addUserField(self, **kwargs):
        self.fields[lowest_user_field_idx] = SymbolField(idx = lowest_user_field_idx, **kwargs)
        lowest_user_field_idx += 1

    def addAlias(self, alias_name, dcm_options={}):
        self.used_names_in_lib.addName(alias_name)
        self.aliases[alias_name] = DcmEntry(name = alias_name, **dcm_options)

    def addFootprintFilter(self, filter):
        if isinstance(filter, str):
            self.footprint_filter.append(filter)
        elif isinstance(filter, collections.Sequence):
            self.footprint_filter += filter
        else:
            raise TypeError('addFootprintFilter only works for strings and lists of strings.')

    def generateLibContent(self):
        # Write 3 comment lines with the symbol name.
        symbol = '#\n# {name}\n#\n'.format(name=self.symbol_name)
        # DEF name ref 0 offs Y Y 1 F N
        symbol += 'DEF {name:s} {ref:s} 0 {offset:d} {pin_num_visibility:s} {pin_name_visibility:s} {num_units:d} {interchangable:s} {power_symbol:s}\n'.format(
    		name=self.symbol_name, ref=self.ref_des,
            offset = self.pin_name_offset,
            pin_num_visibility = self.pin_number_visibility,
            pin_name_visibility = self.pin_name_visibility,
            num_units = self.num_units, interchangable = self.interchangable,
            power_symbol = self.is_power_symbol)

        symbol += ''.join(map(str, self.fields))
        if len(self.aliases) > 0:
            symbol += 'ALIAS {:s}\n'.format(' '.join(map(str, self.aliases.keys())))
        if len(self.footprint_filter) > 0:
            symbol += '$FPLIST\n'
            for filter in self.footprint_filter:
                symbol += ' {:s}\n'.format(str(filter))
            symbol += '$ENDFPLIST\n'

        symbol += str(self.drawing)
        symbol += 'ENDDEF\n'
        return symbol

    def generateDcmContent(self):
        content = ''
        content += str(self.dcm_entry)
        content += ''.join(map(str, self.aliases.values()))
        return content

    def __str__(self):
        string = '############# Lib File Content #############\n'
        string += self.generateLibContent()
        string = '############################################\n'
        string = '\n############# Lib File Content #############\n'
        string += self.generateLibContent()
        return string

class SymbolGenerator:
    def __init__(self, lib_name = 'new_lib', output_path = './'):
        self.lib_name = lib_name
        self.output_path = output_path
        self.symbols = collections.OrderedDict()
        self.used_names_in_lib = uniqueNameManager()

    def addSymbol(self, symbol_name, **kwargs):
        symbol_name = symbol_name
        if symbol_name in self.symbols.keys():
            return self.symbols[symbol_name]
        else:
            self.used_names_in_lib.addName(symbol_name)
            self.symbols[symbol_name] = Symbol(symbol_name, self.used_names_in_lib, **kwargs)
            return self.symbols[symbol_name]

    def writeFiles(self):
        lib_file_path = self.output_path + self.lib_name + '.lib'
        dcm_file_path = self.output_path + self.lib_name + '.dcm'

        lib_file =open(lib_file_path, "w")
        lib_file.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
        dcm_file =open(dcm_file_path, "w")
        dcm_file.write('EESchema-DOCLIB  Version 2.0\n')
        for symbol_name, symbol in sorted(self.symbols.items()):
            lib_file.write(symbol.generateLibContent())
            dcm_file.write(symbol.generateDcmContent())

        lib_file.write( '#\n#End Library\n')
        lib_file.close()
        dcm_file.write('#\n#End Doc Library\n')
        dcm_file.close()
