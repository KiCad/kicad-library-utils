#!/usr/bin/env python3

import math
import os
import sys

sys.path.append(os.path.join(sys.path[0], '..'))

from KiCadSymbolGenerator import *

generator = SymbolGenerator('SW_DIP')

def generateDIPSwitch(count):
    name = 'SW_DIP_x{:02d}'.format(count)
    refdes = 'SW'
    footprint = ''
    footprintFilter = 'SW?DIP?x{0}*'.format(count)
    description = '{0}x DIP Switch, Single Pole Single Throw (SPST) switch, small symbol'.format(count)
    keywords = 'dip switch'
    datasheet = '~'

    grid_size = 100
    circle_radius = 20
    pin_length = 200
    switch_length = 200
    body_width = 300
    lever_angle = 15
    lever_length = switch_length - circle_radius
    width = switch_length + 2 * pin_length
    left = -width / 2
    body_x = -body_width / 2
    top = -round(count / 2) * grid_size
    height = count * grid_size
    body_height = height + grid_size
    body_y = top - grid_size

    symbol = generator.addSymbol(name,
        dcm_options = {
            'description': description,
            'keywords': keywords,
            'datasheet': datasheet
        },
        footprint_filter = footprintFilter,
        offset = 0,
        pin_name_visibility = Symbol.PinMarkerVisibility.INVISIBLE
    )
    symbol.setReference(refdes,
        at = Point(0, -(body_y - 50))
    )
    symbol.setValue(
        at = Point(0, -(body_y + body_height + 50))
    )

    # Symbol body
    symbol.drawing.append(DrawingRectangle(
        end = Point(body_x + body_width, -(body_y + body_height)),
        fill = ElementFill.FILL_BACKGROUND,
        start = Point(body_x, -body_y),
        unit_idx = 0
    ))

    pin_left = 1
    pin_right = 2 * count
    pin_y = top

    for s in range(1, count + 1):
        # Left pins
        symbol.drawing.append(DrawingPin(
            at = Point(left, -pin_y),
            name = '~',
            number = pin_left,
            orientation = DrawingPin.PinOrientation.RIGHT,
            pin_length = pin_length
        ))
        # Right pins
        symbol.drawing.append(DrawingPin(
            at = Point(left + width, -pin_y),
            name = '~',
            number = pin_right,
            orientation = DrawingPin.PinOrientation.LEFT,
            pin_length = pin_length
        ))
        # Left circles
        symbol.drawing.append(DrawingCircle(
            at = Point(-(switch_length / 2 - circle_radius), -pin_y),
            line_width = 0,
            radius = circle_radius,
            unit_idx = 0
        ))
        # Right circles
        symbol.drawing.append(DrawingCircle(
            at = Point(switch_length / 2 - circle_radius, -pin_y),
            line_width = 0,
            radius = circle_radius,
            unit_idx = 0
        ))
        # Levers
        symbol.drawing.append(DrawingPolyline(
            line_width = 0,
            points = [
                Point(-(switch_length / 2 - circle_radius) + circle_radius * math.cos(lever_angle / 180 * math.pi), -(pin_y - circle_radius * math.sin(lever_angle / 180 * math.pi))),
                Point(-(switch_length / 2 - circle_radius) + lever_length * math.cos(lever_angle / 180 * math.pi), -(pin_y - lever_length * math.sin(lever_angle / 180 * math.pi)))
            ],
            unit_idx = 0
        ))

        pin_left = pin_left + 1
        pin_right = pin_right - 1
        pin_y = pin_y + grid_size

if __name__ == '__main__':
    for i in range(1, 13):
        generateDIPSwitch(i)

    generator.writeFiles()
