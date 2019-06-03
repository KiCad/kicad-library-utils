#!/usr/bin/python3

# sys.path.append(os.path.join(sys.path[0],'..')) # load KiCadSymbolGenerator path
# add KiCadSymbolGenerator to searchpath using export PYTHONPATH="${PYTHONPATH}<absolute path>/autogen/"
import sys, os
sys.path.append(os.path.join(sys.path[0],'..'))
from KiCadSymbolGenerator import *

from collections import namedtuple
from math import sqrt
import re, fnmatch
import argparse

################################  Parameters ##################################
pin_per_row_range = range(1,41)
pin_per_row_range_dual = range(2,41) #for some dual row connectors all numbering schemes generate the same symbol for the 1 pin per row variant.
pin_per_row_range_screw = range(1,21)
pin_range_dual_row_odd_count = range(2,38)

reference_designator = 'J'

pin_grid = 100
pin_spacing_y = 100
pin_length = 150

mp_artwork_to_body = 30
extra_pin_grid = 50

body_width_per_row = 100
body_fill = ElementFill.FILL_BACKGROUND

ref_fontsize = 50
value_fontsize = 50
pin_number_fontsize = 50

body_outline_line_width = 10
inner_graphics_line_width = 6

inner_graphic_width = 50
inner_graphic_male_neutral_height = 10
inner_graphic_female_radius = 20
inner_graphic_screw_radius = 25
inner_graphic_screw_slit_width = 10


filter_terminal_block = ['TerminalBlock*:*']
filter_single_row = ['Connector*:*_1x??{pn_modifier:s}*']
filter_dual_row = ['Connector*:*_2x??{pn_modifier:s}*']

filter_dual_row_odd_count = ['Connector*:*2Rows*Pins{pn_modifier:s}_*', '*FCC*2Rows*Pins{pn_modifier:s}_*']

pinname_update_function = lambda old_name, new_number: 'Pin_{}'.format(new_number)

CONNECTOR = namedtuple("CONNECTOR",[
    'num_rows',
    'pin_per_row_range',
    'odd_count',
    'symbol_name_format',
    'top_pin_number',
    'pin_number_generator',
    'description',
    'keywords',
    'datasheet',
    'default_footprint',
    'footprint_filter',
    'graphic_type',
    'enclosing_rectangle',
    'mirror'
])

num_gen_row_letter_first = lambda old_number: old_number[:1] + str(int(old_number[1:])+1)
num_gen_row_letter_last = lambda old_number: str(int(old_number[:-1])+1) + old_number[-1:]

conn_screw_terminal = {
    'single_row_screw' : CONNECTOR(
        num_rows = 1,
        pin_per_row_range = pin_per_row_range_screw,
        odd_count = False,
        symbol_name_format = 'Screw_Terminal_01x{num_pins_per_row:02d}{suffix:s}',
        top_pin_number = [1],
        pin_number_generator = [lambda old_number: old_number + 1],
        description = 'Generic screw terminal, single row, 01x{num_pins_per_row:02d}',
        keywords = 'screw terminal',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_terminal_block,
        graphic_type = 3, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    )
}

conn_male_female = {
    'single_row_male' : CONNECTOR(
        num_rows = 1,
        pin_per_row_range = pin_per_row_range,
        odd_count = False,
        symbol_name_format = 'Conn_01x{num_pins_per_row:02d}_Male{suffix:s}',
        top_pin_number = [1],
        pin_number_generator = [lambda old_number: old_number + 1],
        description = 'Generic{extra_pin:s} connector, single row, 01x{num_pins_per_row:02d}',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_single_row,
        graphic_type = 1, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = False,
        mirror = True
    ),
    'single_row_female' : CONNECTOR(
        num_rows = 1,
        pin_per_row_range = pin_per_row_range,
        odd_count = False,
        symbol_name_format = 'Conn_01x{num_pins_per_row:02d}_Female{suffix:s}',
        top_pin_number = [1],
        pin_number_generator = [lambda old_number: old_number + 1],
        description = 'Generic{extra_pin:s} connector, single row, 01x{num_pins_per_row:02d}',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_single_row,
        graphic_type = 2, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = False,
        mirror = False
    )
}

conn_generic = {
    'single_row' : CONNECTOR(
        num_rows = 1,
        pin_per_row_range = pin_per_row_range,
        odd_count = False,
        symbol_name_format = 'Conn_01x{num_pins_per_row:02d}{suffix:s}',
        top_pin_number = [1],
        pin_number_generator = [lambda old_number: old_number + 1],
        description = 'Generic{extra_pin:s} connector, single row, 01x{num_pins_per_row:02d}',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_single_row,
        graphic_type = 0, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    ),
    'dual_row_odd-even' : CONNECTOR(
        num_rows = 2,
        pin_per_row_range = pin_per_row_range_dual,
        odd_count = False,
        symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_Odd_Even{suffix:s}',
        top_pin_number = [1, lambda num_pin_per_row: 2],
        pin_number_generator = [lambda old_number: old_number + 2, lambda old_number: old_number + 2],
        description = 'Generic{extra_pin:s} connector, double row, 02x{num_pins_per_row:02d}, odd/even pin numbering scheme (row 1 odd numbers, row 2 even numbers)',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_dual_row,
        graphic_type = 0, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    ),
    'dual_row_counter-clockwise' : CONNECTOR(
        num_rows = 2,
        pin_per_row_range = pin_per_row_range_dual,
        odd_count = False,
        symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_Counter_Clockwise{suffix:s}',
        top_pin_number = [1, lambda num_pin_per_row: 2*num_pin_per_row],
        pin_number_generator = [lambda old_number: old_number + 1, lambda old_number: old_number -1],
        description = 'Generic{extra_pin:s} connector, double row, 02x{num_pins_per_row:02d}, counter clockwise pin numbering scheme (similar to DIP packge numbering)',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_dual_row,
        graphic_type = 0, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    ),
    'dual_row_top-bottom' : CONNECTOR(
        num_rows = 2,
        pin_per_row_range = pin_per_row_range_dual,
        odd_count = False,
        symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_Top_Bottom{suffix:s}',
        top_pin_number = [1, lambda num_pin_per_row: num_pin_per_row + 1],
        pin_number_generator = [lambda old_number: old_number + 1, lambda old_number: old_number +1],
        description = 'Generic{extra_pin:s} connector, double row, 02x{num_pins_per_row:02d}, top/bottom pin numbering scheme (row 1: 1...pins_per_row, row2: pins_per_row+1 ... num_pins)',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_dual_row,
        graphic_type = 0, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    ),
    'dual_row_02x01_numbered' : CONNECTOR(
        num_rows = 2,
        pin_per_row_range = [1],
        odd_count = False,
        symbol_name_format = 'Conn_02x{num_pins_per_row:02d}{suffix:s}',
        top_pin_number = [1, lambda num_pin_per_row: num_pin_per_row + 1],
        pin_number_generator = [lambda old_number: old_number + 1, lambda old_number: old_number +1],
        description = 'Generic{extra_pin:s} connector, double row, 02x01, this symbol is compatible with counter-clockwise, top-bottom and odd-even numbering schemes.',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_dual_row,
        graphic_type = 0, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    ),
    'dual_row_letter-first' : CONNECTOR(
        num_rows = 2,
        pin_per_row_range = pin_per_row_range,
        odd_count = False,
        symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_Row_Letter_First{suffix:s}',
        top_pin_number = ['a1', lambda num_pin_per_row: 'b1'],
        pin_number_generator = [num_gen_row_letter_first, num_gen_row_letter_first],
        description = 'Generic{extra_pin:s} connector, double row, 02x{num_pins_per_row:02d}, row letter first pin numbering scheme (pin number consists of a letter for the row and a number for the pin index in this row. a1, ..., aN; b1, ..., bN)',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_dual_row,
        graphic_type = 0, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    ),
    'dual_row_letter-last' : CONNECTOR(
        num_rows = 2,
        pin_per_row_range = pin_per_row_range,
        odd_count = False,
        symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_Row_Letter_Last{suffix:s}',
        top_pin_number = ['1a', lambda num_pin_per_row: '1b'],
        pin_number_generator = [num_gen_row_letter_last, num_gen_row_letter_last],
        description = 'Generic{extra_pin:s} connector, double row, 02x{num_pins_per_row:02d}, row letter last pin numbering scheme (pin number consists of a letter for the row and a number for the pin index in this row. 1a, ..., Na; 1b, ..., Nb))',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_dual_row,
        graphic_type = 0, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    ),

    'dual_row_odd_pin_count' : CONNECTOR(
        num_rows = 2,
        pin_per_row_range = pin_range_dual_row_odd_count,
        odd_count = True,
        symbol_name_format = 'Conn_2Rows-{num_pins:02d}Pins{suffix:s}',
        top_pin_number = [1, lambda num_pin_per_row: 2],
        pin_number_generator = [lambda old_number: old_number + 2, lambda old_number: old_number + 2],
        description = 'Generic{extra_pin:s} connector, double row, {num_pins:02d} pins, odd/even pin numbering scheme (row 1 odd numbers, row 2 even numbers)',
        keywords = 'connector',
        datasheet = '~', # generic symbol, no datasheet, ~ to make travis happy
        default_footprint = '', # generic symbol, no default footprint
        footprint_filter = filter_dual_row_odd_count,
        graphic_type = 0, # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
        enclosing_rectangle = True,
        mirror = False
    ),
}

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def draw_mp_end(pin_pos, pin_len):
    artwork = Drawing()


    center = pin_pos.translate(
        {'x': 0,'y': pin_len},
        apply_on_copy = True, new_grid = None)

    xd = body_width_per_row/2 - 10

    artwork.append(DrawingPolyline(
        points = [
            Point({'x':center.x - xd, 'y':center.y}),
            Point({'x':center.x + xd, 'y':center.y})
            ],
        line_width = inner_graphics_line_width))

    center_text = center.translate(
        {'x':0, 'y': mp_artwork_to_body/2},
        apply_on_copy = True, new_grid = None)

    artwork.append(DrawingText(
        at=center_text, text="Mounting", size=mp_artwork_to_body-15
    ))

    return artwork



SHIELD_PIN = {
    "number":"SH",
    "name":"Shield",
    'deco':None,
    'offset':0
}

MOUNT_PIN = {
    "number":"MP",
    "name":"MountPin",
    'deco':draw_mp_end,
    'offset':mp_artwork_to_body
}

all_symbols = [{
    'lib_name': 'Connector',
    'symbol_def': merge_dicts(conn_screw_terminal, conn_male_female),
    'extra_pin': None,
    'pn_modifier': '_',
    'suffix': '',
    'extra_pin_descr':''
    },
    {
    'lib_name': 'Connector_Generic',
    'symbol_def': conn_generic,
    'extra_pin': None,
    'pn_modifier': '_',
    'suffix': '',
    'extra_pin_descr':''
    },
    {
    'lib_name': 'Connector_Generic_Shielded',
    'symbol_def': conn_generic,
    'extra_pin': SHIELD_PIN,
    'pn_modifier': '-1SH',
    'suffix': '_Shielded',
    'extra_pin_descr':' shielded'
    },
    {
    'lib_name': 'Connector_Generic_MountingPin',
    'symbol_def': conn_generic,
    'extra_pin': MOUNT_PIN,
    'pn_modifier': '-1MP',
    'suffix': '_MountingPin',
    'extra_pin_descr':' connectable mounting pin'
    }
]

def innerArtwork(type=0):
    artwork = Drawing()

    if type == 0:
        artwork.append(DrawingRectangle(
            start = Point({'x':0, 'y':inner_graphic_male_neutral_height//2}),
            end = Point({'x':inner_graphic_width, 'y':-inner_graphic_male_neutral_height//2}),
            fill = ElementFill.NO_FILL, line_width = inner_graphics_line_width
            ))
    if type == 1:
        from_edge = inner_graphic_width // 3
        artwork.append(DrawingRectangle(
            start = Point({'x':from_edge, 'y':inner_graphic_male_neutral_height//2}),
            end = Point({'x':inner_graphic_width, 'y':-inner_graphic_male_neutral_height//2}),
            fill = ElementFill.FILL_FOREGROUND, line_width = inner_graphics_line_width
            ))
        artwork.append(DrawingPolyline(
            points = [
                Point({'x':0, 'y':0}),
                Point({'x':from_edge, 'y':0})
                ],
            line_width = inner_graphics_line_width
            ))
    if type == 2:
        artwork.append(DrawingArc(
            at = Point({'x':inner_graphic_width, 'y':0}),
            radius = inner_graphic_female_radius,
            angle_start = 901, angle_end = -901,
            line_width = inner_graphics_line_width
            ))
        artwork.append(DrawingPolyline(
            points = [
                Point({'x':0, 'y':0}),
                Point({'x':inner_graphic_width - inner_graphic_female_radius, 'y':0})
                ],
            line_width = inner_graphics_line_width
            ))
    if type == 3:
        center =  Point({'x': body_width_per_row//2, 'y':0})
        artwork.append(DrawingCircle(
            at = center,
            radius = inner_graphic_screw_radius,
            line_width = inner_graphics_line_width
            ))

        p_slit_1 = Point({
            'x':inner_graphic_screw_slit_width//2,
            'y':int(sqrt(inner_graphic_screw_radius**2 - (inner_graphic_screw_slit_width/2)**2))
            }).translate({'x': center.x, 'y':0})
        line1 = DrawingPolyline(
            points = [p_slit_1, p_slit_1.mirrorVertical(apply_on_copy = True)],
            line_width = inner_graphics_line_width
            )
        artwork.append(line1)
        artwork.append(line1.translate(
            distance={'x':-inner_graphic_screw_slit_width, 'y':0},
            apply_on_copy = True
            ))
        artwork.rotate(angle = 45, origin = center)
        #artwork.rotate(angle = 45)
    return artwork


def generateSingleSymbol(generator, series_params, num_pins_per_row, lib_params):
    pincount = series_params.num_rows * num_pins_per_row + (1 if series_params.odd_count else 0)
    symbol_name = series_params.symbol_name_format.format(
        num_pins_per_row=num_pins_per_row, suffix=lib_params.get('suffix',""),
        num_pins=pincount)

    fp_filter = [filter.format(pn_modifier=lib_params.get("pn_modifier",''))
            for filter in series_params.footprint_filter]

    current_symbol = generator.addSymbol(
        symbol_name, footprint_filter = fp_filter,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE,
        dcm_options = {
        'description':series_params.description.format(
            num_pins_per_row = num_pins_per_row,
            num_pins=pincount,
            extra_pin = lib_params.get('extra_pin_descr','')
            ) + ', script generated (kicad-library-utils/schlib/autogen/connector/)',
        'keywords':series_params.keywords,
        'datasheet':series_params.datasheet
        })



    ########################## reference points ################################
    num_pins_left_side = num_pins_per_row + (1 if series_params.odd_count else 0)

    top_left_pin_position = Point({
        'x': -pin_length - body_width_per_row,
        'y': pin_spacing_y * (num_pins_left_side - 1) / 2.0
        }, grid = pin_grid)

    if series_params.num_rows == 2:
        top_right_pin_position = top_left_pin_position.translate({
            'x': 2*pin_length + 2*body_width_per_row,
            'y': 0
            }, apply_on_copy = True)

    body_top_left_corner = top_left_pin_position.translate({
        'x': pin_length,
        'y': pin_spacing_y/2
        }, apply_on_copy = True, new_grid = None)

    body_width = pin_spacing_y * series_params.num_rows
    body_bottom_right_corner = body_top_left_corner.translate({
        'x': body_width,
        'y': -pin_spacing_y * num_pins_left_side
        }, apply_on_copy = True)

    extra_pin=lib_params.get('extra_pin')

    if extra_pin:
        extra_pin_pos = body_bottom_right_corner.translate(
            {'x': -body_width/2,'y': -pin_length},
            apply_on_copy = True, new_grid = extra_pin_grid)
        extra_pin_length = body_bottom_right_corner.y - extra_pin_pos.y - extra_pin['offset']

    if extra_pin == SHIELD_PIN:
        shield_top_left_corner = body_top_left_corner
        shield_bottom_right_corner = body_bottom_right_corner

        body_top_left_corner = shield_top_left_corner.translate(
            {'x': 10,'y': -10},
            apply_on_copy = True, new_grid = None)
        body_bottom_right_corner = shield_bottom_right_corner.translate(
            {'x': -10,'y': 10},
            apply_on_copy = True, new_grid = None)

    ############################ symbol fields #################################
    ref_pos = body_top_left_corner.translate({'x': body_width/2, 'y':ref_fontsize}, apply_on_copy = True)
    current_symbol.setReference(ref_des = reference_designator,
        at = ref_pos, fontsize = ref_fontsize)

    value_pos = body_bottom_right_corner.translate(
        {'x': -body_width/2 + (50 if extra_pin else 0),
        'y':-ref_fontsize},
        apply_on_copy = True)

    current_symbol.setValue(at = value_pos, fontsize = ref_fontsize,
        alignment_vertical = SymbolField.FieldAlignment.LEFT if extra_pin else SymbolField.FieldAlignment.CENTER)

    ############################ artwork #################################
    drawing = current_symbol.drawing
    if series_params.enclosing_rectangle:
        drawing.append(DrawingRectangle(
            start=body_top_left_corner, end=body_bottom_right_corner,
            line_width = body_outline_line_width, fill = body_fill))

    if extra_pin == SHIELD_PIN:
        drawing.append(DrawingRectangle(
            start=shield_top_left_corner, end=shield_bottom_right_corner,
            line_width = inner_graphics_line_width, fill = ElementFill.NO_FILL))

    if extra_pin:
        drawing.append(DrawingPin(
            at=extra_pin_pos,
            number = extra_pin['number'], name = extra_pin['name'],
            pin_length = extra_pin_length,
            orientation = DrawingPin.PinOrientation.UP
            ))
        if extra_pin['deco']:
            drawing.append(extra_pin['deco'](extra_pin_pos, extra_pin_length))

    repeated_drawing = [innerArtwork(series_params.graphic_type)]

    if series_params.num_rows == 2:
        repeated_drawing.append(repeated_drawing[0]\
            .mirrorHorizontal(apply_on_copy = True)\
            .translate({'x':body_bottom_right_corner.x,'y':top_right_pin_position.y}))
    repeated_drawing[0].translate({'x':body_top_left_corner.x,'y':top_left_pin_position.y})

    pin_number_0 = series_params.top_pin_number[0]
    pin_name_0 = pinname_update_function(None, pin_number_0)
    repeated_drawing[0].append(DrawingPin(
        at=top_left_pin_position,
        number = pin_number_0, name = pin_name_0,
        pin_length = pin_length + (10 if extra_pin==SHIELD_PIN else 0),
        orientation = DrawingPin.PinOrientation.RIGHT
        ))

    if series_params.num_rows == 2:
        pin_number_1 = series_params.top_pin_number[1](num_pins_per_row)
        pin_name_1 = pinname_update_function(None, pin_number_1)
        repeated_drawing[1].append(DrawingPin(
            at = top_right_pin_position,
            number = pin_number_1, name = pin_name_1,
            pin_length = pin_length + (10 if extra_pin==SHIELD_PIN else 0),
            orientation = DrawingPin.PinOrientation.LEFT
            ))


    drawing.append(DrawingArray(
        original = repeated_drawing[0],
        distance = {'x':0, 'y':-pin_spacing_y},
        number_of_instances = num_pins_left_side,
        pinnumber_update_function = series_params.pin_number_generator[0],
        pinname_update_function = pinname_update_function
        ))

    if series_params.num_rows == 2:
        drawing.append(DrawingArray(
            original = repeated_drawing[1],
            distance = {'x':0, 'y':-pin_spacing_y},
            number_of_instances = num_pins_per_row,
            pinnumber_update_function = series_params.pin_number_generator[1],
            pinname_update_function = pinname_update_function
            ))

    if series_params.mirror:
        drawing.mirrorHorizontal()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generator for Generic{extra_pin:s} connector symbols')
    parser.add_argument('--filter', type=str, nargs='?', help='what symbols should be generated', default='*')
    args = parser.parse_args()

    modelfilter = args.filter
    libname = 'conn_new'
    for arg in sys.argv[1:]:
        if arg.startswith("sf="):
            modelfilter = arg[len("sf="):]
        if arg.startswith("o="):
            libname = arg[len("o="):]

    if len(modelfilter) == 0:
        modelfilter = "*"

    model_filter_regobj=re.compile(fnmatch.translate(modelfilter))

    for lib in all_symbols:
        generator = SymbolGenerator(lib['lib_name'])
        print(lib['lib_name'])
        for series_name, series_params in lib['symbol_def'].items():
            if model_filter_regobj.match(series_name):
                for num_pins_per_row in series_params.pin_per_row_range:
                    generateSingleSymbol(generator, series_params, num_pins_per_row, lib)
        generator.writeFiles()
