#!/usr/bin/env python3

import math
import os
import sys

sys.path.append(os.path.join(sys.path[0], '..'))

from KiCadSymbolGenerator import *

def roundToGrid(x, g):
    if x > 0:
        return math.ceil(x / g) * g
    else:
        return math.floor(x / g) * g

generator = SymbolGenerator('R_Network')

def generateResistorNetwork(count):
    name = 'R_Network{:02d}'.format(count)
    refdes = 'RN'
    footprint = 'Resistor_THT:R_Array_SIP{0}'.format(count + 1)
    footprint_filter = 'R?Array?SIP*'
    description = '{0} resistor network, star topology, bussed resistors, small symbol'.format(count)
    keywords = 'R network star-topology'
    datasheet = 'http://www.vishay.com/docs/31509/csc.pdf'

    grid_size = 100
    junction_diameter = 20
    pin_length = 100
    resistor_length = 160
    resistor_width = 60
    resistor_top_lead_length = 30
    body_left_offset = 50
    left = -math.floor(count / 2) * grid_size
    body_x = left - body_left_offset
    body_y = -125
    body_height = 250
    body_width = (count - 1) * grid_size + 2 * body_left_offset
    top = -200
    bottom = 200

    symbol = generator.addSymbol(name,
        dcm_options = {
            'datasheet': datasheet,
            'description': description,
            'keywords': keywords
        },
        footprint_filter = footprint_filter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = Point(body_x - 50, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setValue(
        at = Point(body_x + body_width + 50, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setDefaultFootprint(
        at = Point(body_x + body_width + 50 + 75, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL,
        value = footprint
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = Point(body_x + body_width, body_y + body_height),
        fill = ElementFill.FILL_BACKGROUND,
        start = Point(body_x, body_y),
        unit_idx = 0
    ))

    pin_left = left

    # Common pin
    symbol.drawing.append(DrawingPin(
        at = Point(pin_left, -top),
        name = 'common',
        number = 1,
        orientation = DrawingPin.PinOrientation.DOWN,
        pin_length = pin_length
    ))

    # First top resistor lead
    symbol.drawing.append(DrawingPolyline(
        line_width = 0,
        points = [
            Point(pin_left, -(top + pin_length)),
            Point(pin_left, -(bottom - pin_length - resistor_length))
        ],
        unit_idx = 0
    ))

    for s in range(1, count + 1):
        # Resistor pins
        symbol.drawing.append(DrawingPin(
            at = Point(pin_left, -bottom),
            name = 'R{0}'.format(s),
            number = s + 1,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pin_length
        ))
        # Resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = Point(pin_left + resistor_width / 2, -(bottom - pin_length)),
            start = Point(pin_left - resistor_width / 2, -(bottom - pin_length - resistor_length)),
            unit_idx = 0
        ))

        if s < count:
            # Top resistor leads
            symbol.drawing.append(DrawingPolyline(
                line_width = 0,
                points = [
                    Point(pin_left, -(bottom - pin_length - resistor_length)),
                    Point(pin_left, -(bottom - pin_length - resistor_length - resistor_top_lead_length)),
                    Point(pin_left + grid_size, -(bottom - pin_length - resistor_length - resistor_top_lead_length)),
                    Point(pin_left + grid_size, -(bottom - pin_length - resistor_length))
                ],
                unit_idx = 0
            ))
            # Junctions
            symbol.drawing.append(DrawingCircle(
                at = Point(pin_left, -(bottom - pin_length - resistor_length - resistor_top_lead_length)),
                fill = ElementFill.FILL_FOREGROUND,
                line_width = 0,
                radius = junction_diameter / 2,
                unit_idx = 0
            ))

        pin_left = pin_left + grid_size

def generateSIPNetworkDividers(count):
    name = 'R_Network_Dividers_x{:02d}_SIP'.format(count)
    refdes = 'RN'
    footprint = 'Resistor_THT:R_Array_SIP{0}'.format(count + 2)
    footprint_filter = 'R?Array?SIP*'
    description = '{0} voltage divider network, dual terminator, SIP package'.format(count)
    keywords = 'R network divider topology'
    datasheet = 'http://www.vishay.com/docs/31509/csc.pdf'

    grid_size = 200
    junction_diameter = 20
    pin_length = 100
    resistor_length = 100
    resistor_width = 40
    body_left_offset = 50
    left = -math.floor(count / 2) * grid_size
    top = -300
    bottom = 300
    body_x = left - body_left_offset
    body_y = top + pin_length
    body_height = abs(bottom - pin_length - body_y)
    body_width = (count - 1) * grid_size + grid_size / 2 + 2 * body_left_offset
    resistor_vertical_spacing = (body_height - 2 * resistor_length) / 3

    symbol = generator.addSymbol(name,
        dcm_options = {
            'datasheet': datasheet,
            'description': description,
            'keywords': keywords
        },
        footprint_filter = footprint_filter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = Point(body_x - 50, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setValue(
        at = Point(body_x + body_width + 50, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setDefaultFootprint(
        at = Point(body_x + body_width + 50 + 75, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL,
        value = footprint
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = Point(body_x + body_width, body_y + body_height),
        fill = ElementFill.FILL_BACKGROUND,
        start = Point(body_x, body_y),
        unit_idx = 0
    ))

    pin_left = left

    # Common 1 pin
    symbol.drawing.append(DrawingPin(
        at = Point(pin_left, -top),
        name = 'COM1',
        number = 1,
        orientation = DrawingPin.PinOrientation.DOWN,
        pin_length = pin_length
    ))
    # Common 2 pin
    symbol.drawing.append(DrawingPin(
        at = Point(left + (count - 1) * grid_size + grid_size / 2, -top),
        name = 'COM2',
        number = count + 2,
        orientation = DrawingPin.PinOrientation.DOWN,
        pin_length = pin_length
    ))
    # Vertical COM2 lead
    symbol.drawing.append(DrawingPolyline(
        line_width = 0,
        points = [
            Point(left + (count - 1) * grid_size + grid_size / 2, -(bottom - pin_length - resistor_vertical_spacing / 2)),
            Point(left + (count - 1) * grid_size + grid_size / 2, -(top + pin_length))
        ],
        unit_idx = 0
    ))

    for s in range(1, count + 1):
        # Voltage divider center pins
        symbol.drawing.append(DrawingPin(
            at = Point(pin_left, -bottom),
            name = 'R{0}'.format(s),
            number = s + 1,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pin_length
        ))
        # Top resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = Point(pin_left + resistor_width / 2, -(top + pin_length + resistor_vertical_spacing + resistor_length)),
            start = Point(pin_left - resistor_width / 2, -(top + pin_length + resistor_vertical_spacing)),
            unit_idx = 0
        ))
        # Bottom resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = Point(pin_left + 3 * resistor_width / 2 + resistor_width / 2, -(bottom - pin_length - resistor_vertical_spacing - resistor_length)),
            start = Point(pin_left + 3 * resistor_width / 2 - resistor_width / 2, -(bottom - pin_length - resistor_vertical_spacing)),
            unit_idx = 0
        ))
        # Horizontal COM2 leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                Point(pin_left + 3 * resistor_width / 2, -(bottom - pin_length - resistor_vertical_spacing)),
                Point(pin_left + 3 * resistor_width / 2, -(bottom - pin_length - resistor_vertical_spacing / 2)),
                Point(left + (count - 1) * grid_size + grid_size / 2, -(bottom - pin_length - resistor_vertical_spacing / 2))
            ],
            unit_idx = 0
        ))

        if s == 1:
            # First resistor top lead
            symbol.drawing.append(DrawingPolyline(
                line_width = 0,
                points = [
                    Point(pin_left, -(top + pin_length)),
                    Point(pin_left, -(top + pin_length + resistor_vertical_spacing))
                ],
                unit_idx = 0
            ))

        if s > 1:
            # Top resistor top leads
            symbol.drawing.append(DrawingPolyline(
                line_width = 0,
                points = [
                    Point(pin_left - grid_size, -(top + pin_length + resistor_vertical_spacing / 2)),
                    Point(pin_left, -(top + pin_length + resistor_vertical_spacing / 2)),
                    Point(pin_left, -(top + pin_length + resistor_vertical_spacing))
                ],
                unit_idx = 0
            ))

        # Top resistor bottom leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                Point(pin_left, -(bottom - pin_length)),
                Point(pin_left, -(top + pin_length + resistor_vertical_spacing + resistor_length))
            ],
            unit_idx = 0
        ))
        # Bottom resistor top leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                Point(pin_left, -(top + pin_length + resistor_vertical_spacing + resistor_length + resistor_vertical_spacing / 2)),
                Point(pin_left + 3 * resistor_width / 2, -(top + pin_length + resistor_vertical_spacing + resistor_length + resistor_vertical_spacing / 2)),
                Point(pin_left + 3 * resistor_width / 2, -(bottom - pin_length - resistor_vertical_spacing - resistor_length))
            ],
            unit_idx = 0
        ))
        # Center junctions
        symbol.drawing.append(DrawingCircle(
            at = Point(pin_left, 0),
            fill = ElementFill.FILL_FOREGROUND,
            line_width = 0,
            radius = junction_diameter / 2,
            unit_idx = 0
        ))

        if s > 1:
            # Bottom junctions
            symbol.drawing.append(DrawingCircle(
                at = Point(pin_left + 3 * resistor_width / 2, -(bottom - pin_length - resistor_vertical_spacing / 2)),
                fill = ElementFill.FILL_FOREGROUND,
                line_width = 0,
                radius = junction_diameter / 2,
                unit_idx = 0
            ))

        if s < count:
            # Top junctions
            symbol.drawing.append(DrawingCircle(
                at = Point(pin_left, -(top + pin_length + resistor_vertical_spacing / 2)),
                fill = ElementFill.FILL_FOREGROUND,
                line_width = 0,
                radius = junction_diameter / 2,
                unit_idx = 0
            ))

        pin_left = pin_left + grid_size

def generateResistorPack(count):
    name = 'R_Pack{:02d}'.format(count)
    refdes = 'RN'
    footprint = ''
    footprint_filter = ['DIP*', 'SOIC*']
    description = '{0} resistor network, parallel topology, DIP package'.format(count)
    keywords = 'R network parallel topology isolated'
    datasheet = '~'

    grid_size = 100
    pin_length = 100
    resistor_length = 150
    resistor_width = 50
    body_left_offset = 50
    body_top_offset = 20
    left = -roundToGrid(((count - 1) * grid_size) / 2, 100)
    body_x = left - body_left_offset
    body_height = resistor_length + 2 * body_top_offset
    body_y = -body_height / 2
    body_width = ((count - 1) * grid_size) + 2 * body_left_offset
    top = -200
    bottom = 200

    symbol = generator.addSymbol(name,
        dcm_options = {
            'datasheet': datasheet,
            'description': description,
            'keywords': keywords
        },
        footprint_filter = footprint_filter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = Point(body_x - 50, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setValue(
        at = Point(body_x + body_width + 50, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setDefaultFootprint(
        at = Point(body_x + body_width + 50 + 75, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL,
        value = footprint
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = Point(body_x + body_width, body_y + body_height),
        fill = ElementFill.FILL_BACKGROUND,
        start = Point(body_x, body_y),
        unit_idx = 0
    ))

    pin_left = left

    for s in range(1, count + 1):
        # Resistor bottom pins
        symbol.drawing.append(DrawingPin(
            at = Point(pin_left, -bottom),
            name = 'R{0}.1'.format(s),
            number = s,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pin_length
        ))
        # Resistor top pins
        symbol.drawing.append(DrawingPin(
            at = Point(pin_left, -top),
            name = 'R{0}.2'.format(s),
            number = 2 * count - s + 1,
            orientation = DrawingPin.PinOrientation.DOWN,
            pin_length = pin_length
        ))
        # Resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = Point(pin_left + resistor_width / 2, -(resistor_length / 2)),
            start = Point(pin_left - resistor_width / 2, -(-resistor_length / 2)),
            unit_idx = 0
        ))
        # Resistor bottom leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                Point(pin_left, -(bottom - pin_length)),
                Point(pin_left, -(resistor_length / 2))
            ],
            unit_idx = 0
        ))
        # Resistor top leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                Point(pin_left, -(-resistor_length / 2)),
                Point(pin_left, -(top + pin_length))
            ],
            unit_idx = 0
        ))

        pin_left = pin_left + grid_size

def generateSIPResistorPack(count):
    name = 'R_Pack{:02d}_SIP'.format(count)
    refdes = 'RN'
    footprint = 'Resistor_THT:R_Array_SIP{0}'.format(count * 2)
    footprint_filter = 'R?Array?SIP*'
    description = '{0} resistor network, parallel topology, SIP package'.format(count)
    keywords = 'R network parallel topology isolated'
    datasheet = 'http://www.vishay.com/docs/31509/csc.pdf'

    grid_size = 100
    resistor_horizontal_spacing = 300
    pin_length = 150
    resistor_length = 160
    resistor_width = 60
    resistor_long_lead_length = 30
    body_left_offset = 50
    left = -roundToGrid(((count - 1) * resistor_horizontal_spacing) / 2, 100)
    body_x = left - body_left_offset
    body_y = -75
    body_height = 250
    body_width = ((count - 1) * resistor_horizontal_spacing + grid_size) + 2 * body_left_offset
    bottom = 200

    symbol = generator.addSymbol(name,
        dcm_options = {
            'datasheet': datasheet,
            'description': description,
            'keywords': keywords
        },
        footprint_filter = footprint_filter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = Point(body_x - 50, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setValue(
        at = Point(body_x + body_width + 50, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setDefaultFootprint(
        at = Point(body_x + body_width + 50 + 75, 0),
        orientation = SymbolField.FieldOrientation.VERTICAL,
        value = footprint
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = Point(body_x + body_width, body_y + body_height),
        fill = ElementFill.FILL_BACKGROUND,
        start = Point(body_x, body_y),
        unit_idx = 0
    ))

    pin_left = left

    for s in range(1, count + 1):
        # Resistor short pins
        symbol.drawing.append(DrawingPin(
            at = Point(pin_left, -bottom),
            name = 'R{0}.1'.format(s),
            number = 2 * s - 1,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pin_length
        ))
        # Resistor long pins
        symbol.drawing.append(DrawingPin(
            at = Point(pin_left + grid_size, -bottom),
            name = 'R{0}.2'.format(s),
            number = 2 * s,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pin_length
        ))
        # Resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = Point(pin_left + resistor_width / 2, -(bottom - pin_length)),
            start = Point(pin_left - resistor_width / 2, -(bottom - pin_length - resistor_length)),
            unit_idx = 0
        ))
        # Resistor long leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                Point(pin_left, -(bottom - pin_length - resistor_length)),
                Point(pin_left, -(bottom - pin_length - resistor_length - resistor_long_lead_length)),
                Point(pin_left + grid_size, -(bottom - pin_length - resistor_length - resistor_long_lead_length)),
                Point(pin_left + grid_size, -(bottom - pin_length))
            ],
            unit_idx = 0
        ))

        pin_left = pin_left + resistor_horizontal_spacing

if __name__ == '__main__':
    for i in range(3, 14):
        generateResistorNetwork(i)

    for i in range(2, 12):
        generateSIPNetworkDividers(i)

    for i in range(2, 8):
        generateResistorPack(i)
        generateSIPResistorPack(i)

    for i in range(8, 12):
        generateResistorPack(i)

    generator.writeFiles()
