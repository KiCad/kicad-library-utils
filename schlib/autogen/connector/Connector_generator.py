#!/usr/bin/python3

# sys.path.append(os.path.join(sys.path[0],'..')) # load KiCadSymbolGenerator path
# add KiCadSymbolGenerator to searchpath using export PYTHONPATH="${PYTHONPATH}<absolute path>/autogen/"
import sys, os
sys.path.append(os.path.join(sys.path[0],'..'))
from KiCadSymbolGenerator import *

from collections import namedtuple
from math import sqrt

################################  Parameters ##################################
pin_per_row_range = [2]

reference_designator = 'J'

pin_grid = 100
pin_spacing_y = 100
pin_lenght = 150

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

filter_terminal_block = ['Connector*Terminal*Block*:*']
filter_single_row = ['Connector*:*']
filter_dual_row = ['Connector*:*_02x*']

CONNECTOR = namedtuple("CONNECTOR",[
	'num_rows',
	'pin_per_row_range',
    'symbol_name_format',
	'pin_number_generator',
	'description',
	'keywords',
	'datasheet',
	'default_footprint',
	'footprint_filter',
	'graphic_type'
])

connector_params = {
	# 'single_row_screw' : CONNECTOR(
	# 	num_rows = 1,
	# 	pin_per_row_range = pin_per_row_range,
	# 	symbol_name_format = 'Screw_Terminal_01x{num_pins_per_row:02d}',
	# 	pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx),
	# 	description = 'Generic screw terminal, single row, 01x{num_pins_per_row:02d}',
	# 	keywords = 'screw terminal',
	# 	datasheet = '', # generic symbol, no datasheet
	# 	default_footprint = '', # generic symbol, no default footprint
	# 	footprint_filter = filter_terminal_block,
	# 	graphic_type = 3 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	# ),
	# 'single_row' : CONNECTOR(
	# 	num_rows = 1,
	# 	pin_per_row_range = pin_per_row_range,
	# 	symbol_name_format = 'Conn_01x{num_pins_per_row:02d}',
	# 	pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx),
	# 	description = 'Generic connector, single row, 01x{num_pins_per_row:02d}',
	# 	keywords = 'connector',
	# 	datasheet = '', # generic symbol, no datasheet
	# 	default_footprint = '', # generic symbol, no default footprint
	# 	footprint_filter = filter_single_row,
	# 	graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	# ),
	# 'single_row_male' : CONNECTOR(
	# 	num_rows = 1,
	# 	pin_per_row_range = pin_per_row_range,
	# 	symbol_name_format = 'Conn_Male_01x{num_pins_per_row:02d}',
	# 	pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx),
	# 	description = 'Generic connector, single row, 01x{num_pins_per_row:02d}',
	# 	keywords = 'connector',
	# 	datasheet = '', # generic symbol, no datasheet
	# 	default_footprint = '', # generic symbol, no default footprint
	# 	footprint_filter = filter_single_row,
	# 	graphic_type = 1 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	# ),
	# 'single_row_female' : CONNECTOR(
	# 	num_rows = 1,
	# 	pin_per_row_range = pin_per_row_range,
	# 	symbol_name_format = 'Conn_Female_01x{num_pins_per_row:02d}',
	# 	pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx),
	# 	description = 'Generic connector, single row, 01x{num_pins_per_row:02d}',
	# 	keywords = 'connector',
	# 	datasheet = '', # generic symbol, no datasheet
	# 	default_footprint = '', # generic symbol, no default footprint
	# 	footprint_filter = filter_single_row,
	# 	graphic_type = 2 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	# ),
	'dualrow_odd-even' : CONNECTOR(
		num_rows = 2,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_odd-even',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(2*pin_idx if row_idx == 2 else 2*pin_idx - 1),
		description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, odd/even pin numbering scheme (row 1 odd numbers, row 2 even numbers)',
		keywords = 'connector',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_dual_row,
		graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	),
	# 'dualrow_counter-clockwise' : CONNECTOR(
	# 	num_rows = 2,
	# 	pin_per_row_range = pin_per_row_range,
	# 	symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_counter-clockwise',
	# 	pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx if row_idx == 1 else 2*pins_per_row - (pin_idx - 1)),
	# 	description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, counter clockwise pin numbering scheme (similar to DIP packge numbering)',
	# 	keywords = 'connector',
	# 	datasheet = '', # generic symbol, no datasheet
	# 	default_footprint = '', # generic symbol, no default footprint
	# 	footprint_filter = filter_dual_row,
	# 	graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	# ),
	# 'dualrow_top-bottom' : CONNECTOR(
	# 	num_rows = 2,
	# 	pin_per_row_range = pin_per_row_range,
	# 	symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_top-bottom',
	# 	pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx if row_idx == 1 else pins_per_row + pin_idx),
	# 	description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, top/bottom pin numbering scheme (row 1: 1...pins_per_row, row2: pins_per_row+1 ... num_pins)',
	# 	keywords = 'connector',
	# 	datasheet = '', # generic symbol, no datasheet
	# 	default_footprint = '', # generic symbol, no default footprint
	# 	footprint_filter = filter_dual_row,
	# 	graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	# ),
	# 'conn_02xPP_row-letter-first' : CONNECTOR(
	# 	num_rows = 2,
	# 	pin_per_row_range = pin_per_row_range,
	# 	symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_row-letter-first',
	# 	pin_number_generator = lambda row_idx, pin_idx, pins_per_row:'{letter}{num:d}'.format(
	# 		letter = 'a' if row_idx == 1 else 'b', num = pin_idx),
	# 	description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, row letter first pin numbering scheme (pin number consists of a letter for the row and a number for the pin index in this row. a1, ..., aN; b1, ..., bN)',
	# 	keywords = 'connector',
	# 	datasheet = '', # generic symbol, no datasheet
	# 	default_footprint = '', # generic symbol, no default footprint
	# 	footprint_filter = filter_dual_row,
	# 	graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	# ),
	# 'conn_02xPP_row-letter-last' : CONNECTOR(
	# 	num_rows = 2,
	# 	pin_per_row_range = pin_per_row_range,
	# 	symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_row-letter-last',
	# 	pin_number_generator = lambda row_idx, pin_idx, pins_per_row:'{num:d}{letter}'.format(
	# 		letter = 'a' if row_idx == 1 else 'b', num = pin_idx),
	# 	description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, row letter last pin numbering scheme (pin number consists of a letter for the row and a number for the pin index in this row. 1a, ..., Na; 1b, ..., Nb))',
	# 	keywords = 'connector',
	# 	datasheet = '', # generic symbol, no datasheet
	# 	default_footprint = '', # generic symbol, no default footprint
	# 	footprint_filter = filter_dual_row,
	# 	graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	# )
}

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
        artwork.append(DrawingCircle(
            at = Point({'x': inner_graphic_width/2, 'y':0}),
            radius = inner_graphic_screw_radius,
            line_width = inner_graphics_line_width
            ))

        p_slit_1 = Point({
            'x':inner_graphic_screw_slit_width//2,
            'y':int(sqrt(inner_graphic_screw_radius**2 - (inner_graphic_screw_slit_width/2)**2))
            }).translate({'x': inner_graphic_width/2, 'y':0})
        line1 = DrawingPolyline(
            points = [p_slit_1, p_slit_1.mirrorVertical(apply_on_copy = True)],
            line_width = inner_graphics_line_width
            )
        artwork.append(line1)
        artwork.append(line1.translate(
            distance={'x':-inner_graphic_screw_slit_width, 'y':0},
            apply_on_copy = True
            ))
        artwork.rotate(angle = 45, origin = {'x': inner_graphic_width/2, 'y':0})
        #artwork.rotate(angle = 45)
    return artwork


def generateSingleSymbol(generator, series_params, num_pins_per_row):
    symbol_name = series_params.symbol_name_format.format(num_pins_per_row=num_pins_per_row)
    current_symbol = generator.addSymbol(
        symbol_name, footprint_filter = series_params.footprint_filter,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE)

    ########################## reference points ################################
    top_left_pin_position = Point({
        'x': -pin_lenght - body_width_per_row,
        'y': pin_spacing_y * (num_pins_per_row - 1) / 2.0
        }, grid = pin_grid)

    if series_params.num_rows == 2:
        top_right_pin_position = top_left_pin_position.translate({
            'x': 2*pin_lenght + 2*body_width_per_row,
            'y': 0
            }, apply_on_copy = True)

    body_top_left_corner = top_left_pin_position.translate({
        'x': pin_lenght,
        'y': pin_spacing_y/2
        }, apply_on_copy = True, new_grid = None)

    body_width = pin_spacing_y * num_pins_per_row
    body_bottom_right_corner = body_top_left_corner.translate({
        'x': body_width,
        'y': -pin_spacing_y * num_pins_per_row
        }, apply_on_copy = True)

    ############################ symbol fields #################################
    ref_pos = body_top_left_corner.translate({'x': body_width/2, 'y':ref_fontsize}, apply_on_copy = True)
    current_symbol.setReference(ref_des = reference_designator,
        at = ref_pos, fontsize = ref_fontsize)

    value_pos = body_bottom_right_corner.translate({'x': -body_width/2, 'y':-ref_fontsize}, apply_on_copy = True)
    current_symbol.setValue(at = value_pos, fontsize = ref_fontsize)

    ############################ artwork #################################
    artwork = current_symbol.drawing

    artwork.append(DrawingRectangle(
        start=body_top_left_corner, end=body_bottom_right_corner,
        line_width = body_outline_line_width, fill = body_fill))

    inner_artwork = innerArtwork(series_params.graphic_type)
    artwork.append(inner_artwork)


if __name__ == '__main__':
    generator = SymbolGenerator('conn_new')
    for series_name,series_params in connector_params.items():
        for num_pins_per_row in series_params.pin_per_row_range:
            generateSingleSymbol(generator, series_params, num_pins_per_row)
    generator.writeFiles()
