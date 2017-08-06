#!/usr/bin/python

# Python thingie to write a connector lib for KiCad / EeSchem.
# originally written by P. vd Hoeven.
# 2017-06-18
# https://www.compuphase.com/electronics/LibraryFileFormats.pdf
# Adapted by Poeschl Rene to generate different pin numbering schemes.


from collections import namedtuple
from math import sqrt, cos, sin, floor, ceil, pi
################################  Parameters ##################################
pin_per_row_range = [1,2,5,10]

reference_designator = 'J'

pin_grid = 100
pin_spacing_y = 100
pin_lenght = 150

body_width_per_row = 100
body_fill = 'f' # Fill: N = None, f = fill background (yellow), F = fill foreground (red)

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
	'single_row_screw' : CONNECTOR(
		num_rows = 1,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Screw_Terminal_01x{num_pins_per_row:02d}',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx),
		description = 'Generic screw terminal, single row, 01x{num_pins_per_row:02d}',
		keywords = 'screw terminal',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_terminal_block,
		graphic_type = 3 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	),
	'single_row' : CONNECTOR(
		num_rows = 1,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Conn_01x{num_pins_per_row:02d}',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx),
		description = 'Generic connector, single row, 01x{num_pins_per_row:02d}',
		keywords = 'connector',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_single_row,
		graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	),
	'single_row_male' : CONNECTOR(
		num_rows = 1,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Conn_Male_01x{num_pins_per_row:02d}',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx),
		description = 'Generic connector, single row, 01x{num_pins_per_row:02d}',
		keywords = 'connector',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_single_row,
		graphic_type = 1 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	),
	'single_row_female' : CONNECTOR(
		num_rows = 1,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Conn_Female_01x{num_pins_per_row:02d}',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx),
		description = 'Generic connector, single row, 01x{num_pins_per_row:02d}',
		keywords = 'connector',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_single_row,
		graphic_type = 2 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	),
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
	'dualrow_counter-clockwise' : CONNECTOR(
		num_rows = 2,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_counter-clockwise',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx if row_idx == 1 else 2*pins_per_row - (pin_idx - 1)),
		description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, counter clockwise pin numbering scheme (similar to DIP packge numbering)',
		keywords = 'connector',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_dual_row,
		graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	),
	'dualrow_top-bottom' : CONNECTOR(
		num_rows = 2,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_top-bottom',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:(pin_idx if row_idx == 1 else pins_per_row + pin_idx),
		description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, top/bottom pin numbering scheme (row 1: 1...pins_per_row, row2: pins_per_row+1 ... num_pins)',
		keywords = 'connector',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_dual_row,
		graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	),
	'conn_02xPP_row-letter-first' : CONNECTOR(
		num_rows = 2,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_row-letter-first',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:'{letter}{num:d}'.format(
			letter = 'a' if row_idx == 1 else 'b', num = pin_idx),
		description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, row letter first pin numbering scheme (pin number consists of a letter for the row and a number for the pin index in this row. a1, ..., aN; b1, ..., bN)',
		keywords = 'connector',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_dual_row,
		graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	),
	'conn_02xPP_row-letter-last' : CONNECTOR(
		num_rows = 2,
		pin_per_row_range = pin_per_row_range,
		symbol_name_format = 'Conn_02x{num_pins_per_row:02d}_row-letter-last',
		pin_number_generator = lambda row_idx, pin_idx, pins_per_row:'{num:d}{letter}'.format(
			letter = 'a' if row_idx == 1 else 'b', num = pin_idx),
		description = 'Generic connector, double row, 02x{num_pins_per_row:02d}, row letter last pin numbering scheme (pin number consists of a letter for the row and a number for the pin index in this row. 1a, ..., Na; 1b, ..., Nb))',
		keywords = 'connector',
		datasheet = '', # generic symbol, no datasheet
		default_footprint = '', # generic symbol, no default footprint
		footprint_filter = filter_dual_row,
		graphic_type = 0 # 0 = neutral, 1 = male, 2 = female, 3 = screw terminal
	)
}


class Drawing:
	def __init__(self):
		self.rectangle = []
		self.polyline = []
		self.arc = []
		self.pins = []
		self.circle = []
	def append_pin(self, str):
		self.pins.append(str)
	def append_poly(self, str):
		self.polyline.append(str)
	def append_arc(self, str):
		self.arc.append(str)
	def append_rectangle(self, str):
		self.rectangle.append(str)
	def append_circle(self, str):
		self.circle.append(str)

	def __str__(self):
		drawing = 'DRAW\n'
		drawing += ''.join(self.arc)
		drawing += ''.join(self.circle)
		drawing += ''.join(self.rectangle)
		drawing += ''.join(self.polyline)
		drawing += ''.join(self.pins)
		drawing += 'ENDDRAW\n'
		return drawing


################################ helper functions #############################

def round_to_grid(x, base=pin_grid):
	if x >= 0:
		return floor(x/base) * base
	return ceil(x/base) * base

def rotate(p, angle):
	# angle in rad
    return {
		'x':int(cos(angle) * p['x'] - sin(angle) * p['y']),
		'y':int(sin(angle) * p['x'] + cos(angle) * p['y'])
		}

def translate(p, distance):
	return {
		'x': p['x'] + distance['x'],
		'y': p['y'] + distance['y']
		}
################################ generate symbols #############################

def generate_inner_graphics(drawing, pin_pos_y, body_edge_x, left_side, type=0):
	if type == 0:
		x2 = body_edge_x + (inner_graphic_width if left_side else -inner_graphic_width)
		drawing.append_rectangle('S {x1:d} {y1:d} {x2:d} {y2:d} 0 1 {line_width} {fill}\n'.format(
			x1 = body_edge_x, y1 = pin_pos_y - inner_graphic_male_neutral_height//2,
			x2 = x2, y2 = pin_pos_y + inner_graphic_male_neutral_height//2,
			fill='N', line_width = inner_graphics_line_width))
	if type == 1:
		x2 = body_edge_x + (inner_graphic_width if left_side else -inner_graphic_width)
		from_edge = inner_graphic_width // 3
		drawing.append_rectangle('S {x1:d} {y1:d} {x2:d} {y2:d} 0 1 {line_width} {fill}\n'.format(
			x1 = body_edge_x + (from_edge if left_side else -from_edge),
			y1 = pin_pos_y - inner_graphic_male_neutral_height//2,
			x2 = x2, y2 = pin_pos_y + inner_graphic_male_neutral_height//2,
			fill='F', line_width = inner_graphics_line_width))
		# P 2 0 1 6 -100 50 -70 50 N
		drawing.append_poly('P 2 0 1 {line_width} {x1:d} {pin_y:d} {x2:d} {pin_y:d} N\n'.format(
			x1 = body_edge_x, pin_y = pin_pos_y,
			x2 = body_edge_x + (from_edge if left_side else -from_edge),
			line_width = inner_graphics_line_width
		))
	if type == 2:
		if left_side:
			# A -50 -50 20 901 -901 0 1 6 N -50 -30 -50 -70
			# A -50 50 20 901 -901 0 1 6 N -50 70 -50 30
			drawing.append_arc('A {x:d} {pin_y:d} {r:d} 901 -901 0 1 {line_width} N {x:d} {y1:d} {x:d} {y2:d}\n'.format(
					x = body_edge_x+inner_graphic_width, pin_y = pin_pos_y,
					r = inner_graphic_female_radius, y1 = pin_pos_y + inner_graphic_female_radius,
					y2 = pin_pos_y - inner_graphic_female_radius,
					line_width = inner_graphics_line_width
				))
			# P 2 0 1 6 -100 50 -70 50 N
			drawing.append_poly('P 2 0 1 {line_width} {x1:d} {pin_y:d} {x2:d} {pin_y:d} N\n'.format(
					x1 = body_edge_x, pin_y = pin_pos_y,
					x2 = body_edge_x + (inner_graphic_width - inner_graphic_female_radius)*(1 if left_side else -1),
					line_width = inner_graphics_line_width
				))
		else:
			# A 50 -50 20 -899 899 0 1 6 N 50 -70 50 -30
			# A 50 50 20 -899 899 0 1 6 N 50 30 50 70
			drawing.append_arc('A {x:d} {pin_y:d} {r:d} -899 899 0 1 {line_width} N {x:d} {y1:d} {x:d} {y2:d}\n'.format(
					x = body_edge_x-inner_graphic_width, pin_y = pin_pos_y,
					r = inner_graphic_female_radius, y1 = pin_pos_y - inner_graphic_female_radius,
					y2 = pin_pos_y + inner_graphic_female_radius,
					line_width = inner_graphics_line_width
				))
			# P 2 0 1 6 100 50 70 50 N
			drawing.append_poly('P 2 0 1 {line_width} {x1:d} {pin_y:d} {x2:d} {pin_y:d} N\n'.format(
					x1 = body_edge_x, pin_y = pin_pos_y,
					x2 = body_edge_x - inner_graphic_width + inner_graphic_female_radius,
					line_width = inner_graphics_line_width
				))
	if type == 3:
		# C X Y radius part dmg pen fill
		center = {
			'x': body_edge_x + (body_width_per_row//2)*(1 if left_side else -1),
			'y': pin_pos_y
			}
		drawing.append_circle('C {c_x} {c_y} {r} 0 1 {line_width} N\n'.format(
			c_x = center['x'], c_y = center['y'],
			r = inner_graphic_screw_radius,
			line_width = inner_graphics_line_width
		))

		#calculate points for slit line:
		p_slit_1 = {'x':inner_graphic_screw_slit_width//2,
			'y':int(sqrt(inner_graphic_screw_radius**2 - (inner_graphic_screw_slit_width/2)**2))}
		p_slit_2 = {'x':p_slit_1['x'], 'y':-p_slit_1['y']}
		p_slit_3 = {'x':-p_slit_1['x'], 'y':p_slit_1['y']}
		p_slit_4 = {'x':-p_slit_1['x'], 'y':-p_slit_1['y']}

		p_slit_1 = translate(rotate(p_slit_1, pi/4), center)
		p_slit_2 = translate(rotate(p_slit_2, pi/4), center)
		p_slit_3 = translate(rotate(p_slit_3, pi/4), center)
		p_slit_4 = translate(rotate(p_slit_4, pi/4), center)

		drawing.append_poly('P 2 0 1 {line_width} {x1:d} {y1:d} {x2:d} {y2:d} N\n'.format(
			x1 = p_slit_1['x'], y1 = p_slit_1['y'],
			x2 = p_slit_2['x'], y2 = p_slit_2['y'],
			line_width = inner_graphics_line_width
		))
		drawing.append_poly('P 2 0 1 {line_width} {x1:d} {y1:d} {x2:d} {y2:d} N\n'.format(
			x1 = p_slit_3['x'], y1 = p_slit_3['y'],
			x2 = p_slit_4['x'], y2 = p_slit_4['y'],
			line_width = inner_graphics_line_width
		))


# X name pin X Y length orientation sizenum sizename part dmg type shape
def generate_pin(pin_pos_y, pin_pos_x, left_side, pin_number):
	return 'X P{number} {number} {pos_x:d} {pos_y:d} {length:d} {rot} {fontsize:d} 50 1 1 P\n'.format(
		number=pin_number, pos_x = pin_pos_x,
		pos_y = pin_pos_y, rot = 'R' if left_side else 'L',
		fontsize = pin_number_fontsize, length = pin_lenght)

def generate_connector(num_pins_per_row, series_params, lib_file, dcm_file):
	symbol_name = series_params.symbol_name_format.format(num_pins_per_row=num_pins_per_row)

	dcm_content = '#\n$CMP {name}\n'.format(name=symbol_name)
	dcm_content += 'D {description}\n'.format(description=series_params.description.format(num_pins_per_row=num_pins_per_row))
	dcm_content += 'K {keywords}\n'.format(keywords=series_params.keywords)
	if series_params.datasheet != '':
		dcm_content += 'F {datasheet}\n'.format(datasheet=series_params.datasheet)
	dcm_content += '$ENDCMP\n'
	dcm_file.write(dcm_content)


	top_pin_pos_y = round_to_grid(pin_spacing_y * (num_pins_per_row - 1) / 2.0)
	bottom_pin_pos_y = top_pin_pos_y - (num_pins_per_row - 1) * pin_spacing_y
	row1_pin_x = round_to_grid(-pin_lenght-body_width_per_row)
	row2_pin_x = row1_pin_x + 2*body_width_per_row + 2*pin_lenght
	body_left = row1_pin_x + pin_lenght
	body_right = body_left + (2*body_width_per_row if series_params.num_rows == 2 else body_width_per_row)
	body_center = (body_left + body_right)//2
	# Write 3 comment lines with the symbol name.
	header = '#\n# {name}\n#\n'.format(name=symbol_name)

	# DEF	# Start of symbol definition.
	# name	# If name starts with "~" it is invisible.
	# ref 	# prefix ( J / U / R / C / etc).
	# 0	# Pin name offset in mill from the end-point of a pin
	# YN	# Show/No show for pin numbers.
	# YN	# Show/No show for pin names.
	# 1	# Number of "parts" in a symbol.
	# LF	# "L"ocked or "F" otherwise.
	# PN	" "P"ower symbol or "N" otherwise.
	header += 'DEF {name} {ref} 0 1 Y N 1 F N\n'.format(
		name=symbol_name, ref=reference_designator)

	# F0	# Symoblic prefix text, a mandatory field.
	# ref	# "ref" should be the same as in the "DEF" field.
	# 10 100 50	# X Y & Size of text [mil].
	# HV	# "H"orizonal or "V"ertical Orientation.
	# IV	# "I"nvisible  or "V"isible.
	# Horizontal Alignment	Left Center Right
	# Vertical Alignment	Top Bottom (There are no spaces betweent the last 3 parameters).
	# "I"talic or "N" otherwise.
	# "B"old or "N" otherwise.
	header += 'F0 "{ref}" {pos_x:d} {pos_y:d} {fontsize} H V C CNN\n'.format(
		ref=reference_designator,
		pos_x = body_center, pos_y=top_pin_pos_y + 100,
		fontsize = ref_fontsize)

	#F1	# The symbol name text, a mandatory field. The name  parameter must be the same as in the "DEF" line.
	#	See the "F0" definition for the other parameters.
	header +=  'F1 "{value}" {pos_x:d} {pos_y:d} {fontsize} H V C CNN\n'.format(
		value=symbol_name,
		pos_x = body_center, pos_y = bottom_pin_pos_y - 100,
		fontsize = value_fontsize)

	#F2	# Footprint Field
	#	See the "F0" definition for the other parameters.
	header += 'F2 "{value}" {pos_x:d} {pos_y:d} 50 H I C CNN\n'.format(
		value=series_params.default_footprint,
		pos_x = body_center, pos_y = bottom_pin_pos_y - 200)

	#F3	# Datasheet Field (Not used, use datasheet link in dcm file.)
	#	See the "F0" definition for the other parameters.
	header += 'F3 "" 0 {pos_y:d} 50 H I C CNN\n'.format(pos_y = bottom_pin_pos_y - 300)

	# Add footprint filters if defined:
	# $FPLIST
	#  Filter 1
	#  Filter 2
	#  ...
	# $ENDFPLIST
	if series_params.footprint_filter is not None:
		header += '$FPLIST\n'
		for filter in series_params.footprint_filter:
			header += ' {}\n'.format(filter)
		header += '$ENDFPLIST\n'
	lib_file.write(header)

	drawing = Drawing()

	drawing.append_rectangle('S {x1:d} {y1:d} {x2:d} {y2:d} 0 1 {line_width} {fill}\n'.format(
		x1 = body_left, y1 = top_pin_pos_y + 50,
		x2 = body_right, y2 = bottom_pin_pos_y - 50,
		fill = body_fill, line_width = body_outline_line_width))
	pins = ''
	for row_idx in range(1, series_params.num_rows + 1):
		for pin_idx in range(1, num_pins_per_row + 1):
			pin_pos_y = top_pin_pos_y - (pin_idx - 1)*pin_spacing_y
			generate_inner_graphics(drawing, pin_pos_y, body_left if row_idx == 1 else body_right,
				row_idx == 1, series_params.graphic_type)
			drawing.append_pin(generate_pin(
				pin_pos_y, row1_pin_x if row_idx == 1 else row2_pin_x , row_idx == 1,
				series_params.pin_number_generator(row_idx, pin_idx, num_pins_per_row)))


	lib_file.write(str(drawing))
	lib_file.write('ENDDEF\n')



def generate_connector_series(series_params, lib_file, dcm_file):
	for num_pins_per_row in series_params.pin_per_row_range:
		generate_connector(num_pins_per_row, series_params, lib_file, dcm_file)


if __name__ == '__main__':
	lib_file =open("conn_new.lib", "w")
	lib_file.write("EESchema-LIBRARY Version 2.3\n#encoding utf-8\n")
	dcm_file =open("conn_new.dcm", "w")
	dcm_file.write('EESchema-DOCLIB  Version 2.0\n')
	for series_name,series_params in connector_params.items():
		generate_connector_series(series_params, lib_file, dcm_file)
	lib_file.write( '#\n#End Library\n')
	lib_file.close()
	dcm_file.write('#\n#End Doc Library\n')
	dcm_file.close()
