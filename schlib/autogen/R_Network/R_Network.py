import sys, os
sys.path.append(os.path.join(sys.path[0],'..'))

import math

from KiCadSymbolGenerator import *

def roundG(x, g):
    if x > 0:
        return math.ceil(x / g) * g
    else:
        return math.floor(x / g) * g

generator = SymbolGenerator('R_Network')

def generateResistorNetwork(count):
    name = 'R_Network{:02d}'.format(count)
    refdes = 'RN'
    footprint = 'Resistor_THT:R_Array_SIP{0}'.format(count + 1)
    footprintFilter = 'R?Array?SIP*'
    description = '{0} resistor network, star topology, bussed resistors, small symbol'.format(count)
    keywords = 'R network star-topology'
    datasheet = 'http://www.vishay.com/docs/31509/csc.pdf'

    dp = 100
    pinlen = 100
    R_len = 160
    R_w = 60
    W_dist = 30
    box_l_offset = 50
    left = -math.floor(count / 2) * dp
    l_box = left - box_l_offset
    t_box = -125
    h_box = 250
    w_box = (count - 1) * dp + 2 * box_l_offset
    top = -200
    bottom = 200

    symbol = generator.addSymbol(name,
        dcm_options = {
            'datasheet': datasheet,
            'description': description,
            'keywords': keywords
        },
        footprint_filter = footprintFilter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = {'x': l_box - 50, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setValue(
        at = {'x': l_box + w_box + 50, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setDefaultFootprint(
        at = {'x': l_box + w_box + 50 + 75, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL,
        value = footprint
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = {'x': l_box + w_box, 'y': t_box + h_box},
        fill = ElementFill.FILL_BACKGROUND,
        start = {'x': l_box, 'y': t_box},
        unit_idx = 0
    ))

    pinl = left

    # Common pin
    symbol.drawing.append(DrawingPin(
        at = {'x': pinl, 'y': -top},
        name = 'common',
        number = 1,
        orientation = DrawingPin.PinOrientation.DOWN,
        pin_length = pinlen
    ))

    # First top resistor lead
    symbol.drawing.append(DrawingPolyline(
        line_width = 0,
        points = [
            {'x': pinl, 'y': -(top + pinlen)},
            {'x': pinl, 'y': -(bottom - pinlen - R_len)}
        ],
        unit_idx = 0
    ))

    for s in range(1, count + 1):
        # Resistor pins
        symbol.drawing.append(DrawingPin(
            at = {'x': pinl, 'y': -bottom},
            name = 'R{0}'.format(s),
            number = s + 1,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pinlen
        ))
        # Resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = {'x': pinl + R_w / 2, 'y': -(bottom - pinlen)},
            start = {'x': pinl - R_w / 2, 'y': -(bottom - pinlen - R_len)},
            unit_idx = 0
        ))

        if s < count:
            # Top resistor leads
            symbol.drawing.append(DrawingPolyline(
                line_width = 0,
                points = [
                    {'x': pinl, 'y': -(bottom - pinlen - R_len)},
                    {'x': pinl, 'y': -(bottom - pinlen - R_len - W_dist)},
                    {'x': pinl + dp, 'y': -(bottom - pinlen - R_len - W_dist)},
                    {'x': pinl + dp, 'y': -(bottom - pinlen - R_len)}
                ],
                unit_idx = 0
            ))
            # Junctions
            symbol.drawing.append(DrawingCircle(
                at = {'x': pinl, 'y': -(bottom - pinlen - R_len - W_dist)},
                fill = ElementFill.FILL_FOREGROUND,
                line_width = 0,
                radius = 10,
                unit_idx = 0
            ))

        pinl = pinl + dp

def generateSIPNetworkDividers(count):
    name = 'R_Network_Dividers_x{:02d}_SIP'.format(count)
    refdes = 'RN'
    footprint = 'Resistor_THT:R_Array_SIP{0}'.format(count + 2)
    footprintFilter = 'R?Array?SIP*'
    description = '{0} voltage divider network, dual terminator, SIP package'.format(count)
    keywords = 'R network divider topology'
    datasheet = 'http://www.vishay.com/docs/31509/csc.pdf'

    dp = 200
    dot_diam = 20
    pinlen = 100
    R_len = 100
    R_w = 40
    box_l_offset = 50
    left = -math.floor(count / 2) * dp
    top = -300
    bottom = 300
    l_box = left - box_l_offset
    t_box = top + pinlen
    h_box = abs(bottom - pinlen - t_box)
    w_box = (count - 1) * dp + dp / 2 + 2 * box_l_offset
    R_dist = (h_box - 2 * R_len) / 3

    symbol = generator.addSymbol(name,
        dcm_options = {
            'datasheet': datasheet,
            'description': description,
            'keywords': keywords
        },
        footprint_filter = footprintFilter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = {'x': l_box - 50, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setValue(
        at = {'x': l_box + w_box + 50, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setDefaultFootprint(
        at = {'x': l_box + w_box + 50 + 75, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL,
        value = footprint
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = {'x': l_box + w_box, 'y': t_box + h_box},
        fill = ElementFill.FILL_BACKGROUND,
        start = {'x': l_box, 'y': t_box},
        unit_idx = 0
    ))

    pinl = left

    # Common 1 pin
    symbol.drawing.append(DrawingPin(
        at = {'x': pinl, 'y': -top},
        name = 'COM1',
        number = 1,
        orientation = DrawingPin.PinOrientation.DOWN,
        pin_length = pinlen
    ))
    # Common 2 pin
    symbol.drawing.append(DrawingPin(
        at = {'x': left + (count - 1) * dp + dp / 2, 'y': -top},
        name = 'COM2',
        number = count + 2,
        orientation = DrawingPin.PinOrientation.DOWN,
        pin_length = pinlen
    ))
    # Vertical COM2 lead
    symbol.drawing.append(DrawingPolyline(
        line_width = 0,
        points = [
            {'x': left + (count - 1) * dp + dp / 2, 'y': -(bottom - pinlen - R_dist / 2)},
            {'x': left + (count - 1) * dp + dp / 2, 'y': -(top + pinlen)}
        ],
        unit_idx = 0
    ))

    for s in range(1, count + 1):
        # Voltage divider center pins
        symbol.drawing.append(DrawingPin(
            at = {'x': pinl, 'y': -bottom},
            name = 'R{0}'.format(s),
            number = s + 1,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pinlen
        ))
        # Top resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = {'x': pinl + R_w / 2, 'y': -(top + pinlen + R_dist + R_len)},
            start = {'x': pinl - R_w / 2, 'y': -(top + pinlen + R_dist)},
            unit_idx = 0
        ))
        # Bottom resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = {'x': pinl + 3 * R_w / 2 + R_w / 2, 'y': -(bottom - pinlen - R_dist - R_len)},
            start = {'x': pinl + 3 * R_w / 2 - R_w / 2, 'y': -(bottom - pinlen - R_dist)},
            unit_idx = 0
        ))
        # Horizontal COM2 leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                {'x': pinl + 3 * R_w / 2, 'y': -(bottom - pinlen - R_dist)},
                {'x': pinl + 3 * R_w / 2, 'y': -(bottom - pinlen - R_dist / 2)},
                {'x': left + (count - 1) * dp + dp / 2, 'y': -(bottom - pinlen - R_dist / 2)}
            ],
            unit_idx = 0
        ))

        if s == 1:
            # First resistor top lead
            symbol.drawing.append(DrawingPolyline(
                line_width = 0,
                points = [
                    {'x': pinl, 'y': -(top + pinlen)},
                    {'x': pinl, 'y': -(top + pinlen + R_dist)}
                ],
                unit_idx = 0
            ))

        if s > 1:
            # Top resistor top leads
            symbol.drawing.append(DrawingPolyline(
                line_width = 0,
                points = [
                    {'x': pinl - dp, 'y': -(top + pinlen + R_dist / 2)},
                    {'x': pinl, 'y': -(top + pinlen + R_dist / 2)},
                    {'x': pinl, 'y': -(top + pinlen + R_dist)}
                ],
                unit_idx = 0
            ))

        # Top resistor bottom leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                {'x': pinl, 'y': -(bottom - pinlen)},
                {'x': pinl, 'y': -(top + pinlen + R_dist + R_len)}
            ],
            unit_idx = 0
        ))
        # Bottom resistor top leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                {'x': pinl, 'y': -(top + pinlen + R_dist + R_len + R_dist / 2)},
                {'x': pinl + 3 * R_w / 2, 'y': -(top + pinlen + R_dist + R_len + R_dist / 2)},
                {'x': pinl + 3 * R_w / 2, 'y': -(bottom - pinlen - R_dist - R_len)}
            ],
            unit_idx = 0
        ))
        # Center junctions
        symbol.drawing.append(DrawingCircle(
            at = {'x': pinl, 'y': 0},
            fill = ElementFill.FILL_FOREGROUND,
            line_width = 0,
            radius = dot_diam / 2,
            unit_idx = 0
        ))

        if s > 1:
            # Bottom junctions
            symbol.drawing.append(DrawingCircle(
                at = {'x': pinl + 3 * R_w / 2, 'y': -(bottom - pinlen - R_dist / 2)},
                fill = ElementFill.FILL_FOREGROUND,
                line_width = 0,
                radius = dot_diam / 2,
                unit_idx = 0
            ))

        if s < count:
            # Top junctions
            symbol.drawing.append(DrawingCircle(
                at = {'x': pinl, 'y': -(top + pinlen + R_dist / 2)},
                fill = ElementFill.FILL_FOREGROUND,
                line_width = 0,
                radius = dot_diam / 2,
                unit_idx = 0
            ))

        pinl = pinl + dp

def generateResistorPack(count):
    name = 'R_Pack{:02d}'.format(count)
    refdes = 'RN'
    footprint = ''
    footprintFilter = ['DIP*', 'SOIC*']
    description = '{0} resistor network, parallel topology, DIP package'.format(count)
    keywords = 'R network parallel topology isolated'
    datasheet = '~'

    dp = 100
    pinlen = 100
    R_len = 150
    R_w = 50
    box_l_offset = 50
    box_t_offset = 20
    left = -roundG(((count - 1) * dp) / 2, 100)
    l_box = left - box_l_offset
    h_box = R_len + 2 * box_t_offset
    t_box = -h_box / 2
    w_box = ((count - 1) * dp) + 2 * box_l_offset
    top = -200
    bottom = 200

    symbol = generator.addSymbol(name,
        dcm_options = {
            'datasheet': datasheet,
            'description': description,
            'keywords': keywords
        },
        footprint_filter = footprintFilter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = {'x': l_box - 50, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setValue(
        at = {'x': l_box + w_box + 50, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setDefaultFootprint(
        at = {'x': l_box + w_box + 50 + 75, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL,
        value = footprint
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = {'x': l_box + w_box, 'y': t_box + h_box},
        fill = ElementFill.FILL_BACKGROUND,
        start = {'x': l_box, 'y': t_box},
        unit_idx = 0
    ))

    pinl = left

    for s in range(1, count + 1):
        # Resistor bottom pins
        symbol.drawing.append(DrawingPin(
            at = {'x': pinl, 'y': -bottom},
            name = 'R{0}.1'.format(s),
            number = s,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pinlen
        ))
        # Resistor top pins
        symbol.drawing.append(DrawingPin(
            at = {'x': pinl, 'y': -top},
            name = 'R{0}.2'.format(s),
            number = 2 * count - s + 1,
            orientation = DrawingPin.PinOrientation.DOWN,
            pin_length = pinlen
        ))
        # Resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = {'x': pinl + R_w / 2, 'y': -(R_len / 2)},
            start = {'x': pinl - R_w / 2, 'y': -(-R_len / 2)},
            unit_idx = 0
        ))
        # Resistor bottom leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                {'x': pinl, 'y': -(bottom - pinlen)},
                {'x': pinl, 'y': -(R_len / 2)}
            ],
            unit_idx = 0
        ))
        # Resistor top leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                {'x': pinl, 'y': -(-R_len / 2)},
                {'x': pinl, 'y': -(top + pinlen)}
            ],
            unit_idx = 0
        ))

        pinl = pinl + dp

def generateSIPResistorPack(count):
    name = 'R_Pack{:02d}_SIP'.format(count)
    refdes = 'RN'
    footprint = 'Resistor_THT:R_Array_SIP{0}'.format(count * 2)
    footprintFilter = 'R?Array?SIP*'
    description = '{0} resistor network, parallel topology, SIP package'.format(count)
    keywords = 'R network parallel topology isolated'
    datasheet = 'http://www.vishay.com/docs/31509/csc.pdf'

    dp = 100
    dR = 300
    pinlen = 150
    R_len = 160
    R_w = 60
    W_dist = 30
    box_l_offset = 50
    left = -roundG(((count - 1) * dR) / 2, 100)
    l_box = left - box_l_offset
    t_box = -75
    h_box = 250
    w_box = ((count - 1) * dR + dp) + 2 * box_l_offset
    bottom = 200

    symbol = generator.addSymbol(name,
        dcm_options = {
            'datasheet': datasheet,
            'description': description,
            'keywords': keywords
        },
        footprint_filter = footprintFilter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = {'x': l_box - 50, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setValue(
        at = {'x': l_box + w_box + 50, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL
    )
    symbol.setDefaultFootprint(
        at = {'x': l_box + w_box + 50 + 75, 'y': 0},
        orientation = SymbolField.FieldOrientation.VERTICAL,
        value = footprint
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = {'x': l_box + w_box, 'y': t_box + h_box},
        fill = ElementFill.FILL_BACKGROUND,
        start = {'x': l_box, 'y': t_box},
        unit_idx = 0
    ))

    pinl = left

    for s in range(1, count + 1):
        # Resistor short pins
        symbol.drawing.append(DrawingPin(
            at = {'x': pinl, 'y': -bottom},
            name = 'R{0}.1'.format(s),
            number = 2 * s - 1,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pinlen
        ))
        # Resistor long pins
        symbol.drawing.append(DrawingPin(
            at = {'x': pinl + dp, 'y': -bottom},
            name = 'R{0}.2'.format(s),
            number = 2 * s,
            orientation = DrawingPin.PinOrientation.UP,
            pin_length = pinlen
        ))
        # Resistor bodies
        symbol.drawing.append(DrawingRectangle(
            end = {'x': pinl + R_w / 2, 'y': -(bottom - pinlen)},
            start = {'x': pinl - R_w / 2, 'y': -(bottom - pinlen - R_len)},
            unit_idx = 0
        ))
        # Resistor long leads
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                {'x': pinl, 'y': -(bottom - pinlen - R_len)},
                {'x': pinl, 'y': -(bottom - pinlen - R_len - W_dist)},
                {'x': pinl + dp, 'y': -(bottom - pinlen - R_len - W_dist)},
                {'x': pinl + dp, 'y': -(bottom - pinlen)}
            ],
            unit_idx = 0
        ))

        pinl = pinl + dR

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
