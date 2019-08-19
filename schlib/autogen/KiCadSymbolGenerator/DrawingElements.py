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

from enum import Enum
from KiCadSymbolGenerator.Point import Point
from copy import deepcopy

class ElementFill(Enum):
    NO_FILL = 'N'
    FILL_BACKGROUND = 'f'
    FILL_FOREGROUND = 'F'

    def __str__(self):
        return self.value


class DrawingPin:
    class PinOrientation(Enum):
        UP = 'U'
        DOWN = 'D'
        LEFT = 'L'
        RIGHT = 'R'

        def __str__(self):
            return self.value

    class PinElectricalType(Enum):
        EL_TYPE_INPUT = 'I'
        EL_TYPE_OUTPUT = 'O'
        EL_TYPE_BIDIR = 'B'
        EL_TYPE_TRISTATE = 'T'
        EL_TYPE_PASSIVE = 'P'
        EL_TYPE_OPEN_COLECTOR = 'C'
        EL_TYPE_OPEN_EMITTER = 'E'
        EL_TYPE_NC = 'N'
        EL_TYPE_UNSPECIFIED = 'U'
        EL_TYPE_POWER_INPUT = 'W'
        EL_TYPE_POWER_OUTPUT = 'w'

        def __str__(self):
            return self.value

    class PinVisibility(Enum):
        INVISIBLE = 'N'
        VISIBLE = ''

        def __str__(self):
            return self.value

    class PinStyle(Enum):
        SHAPE_LINE = ''
        SHAPE_INVERTED = 'I'
        SHAPE_CLOCK = 'C'
        SHAPE_INPUT_LOW = 'L'
        SHAPE_OUTPUT_LOW = 'V'
        # There are more, not all are implemented yet.

        def __str__(self):
            return self.value

    def __init__(self, at, number, **kwargs):
        self.at = Point(at)
        self.num = number
        self.name = str(kwargs.get('name', self.num))
        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.pin_length = int(kwargs.get('pin_length', 100))
        self.fontsize_pinnumber = int(kwargs.get('sizenumber', 50))
        self.fontsize_pinname = int(kwargs.get('sizename', self.fontsize_pinnumber))

        el_type = kwargs.get('el_type', DrawingPin.PinElectricalType.EL_TYPE_PASSIVE)
        if isinstance(el_type, DrawingPin.PinElectricalType):
            self.el_type = el_type
        else:
            raise TypeError('el_type needs to be of type PinElectricalType')

        visibility = kwargs.get('visibility', DrawingPin.PinVisibility.VISIBLE)
        if isinstance(visibility, DrawingPin.PinVisibility):
            self.visibility = visibility
        else:
            raise TypeError('visibility needs to be of type PinVisibility')

        style = kwargs.get('style', DrawingPin.PinStyle.SHAPE_LINE)
        if isinstance(style, DrawingPin.PinStyle):
            self.style = style
        else:
            raise TypeError('style needs to be of type PinStyle')

        orientation = kwargs.get('orientation', DrawingPin.PinOrientation.LEFT)
        if isinstance(orientation, DrawingPin.PinOrientation):
            self.orientation = orientation
        else:
            raise TypeError('orientation needs to be of type PinOrientation')

    def updatePinNumber(self, pinnumber_update_function=lambda old_number:old_number+1,
            pinname_update_function = lambda old_name, new_number: new_number):
        self.num = pinnumber_update_function(self.num)
        self.name = pinname_update_function(self.name, self.num)

    def __pinShapeRender(self):
        if self.visibility is DrawingPin.PinVisibility.INVISIBLE or self.style is not DrawingPin.PinStyle.SHAPE_LINE:
            return ' {visibility:s}{style:s}'.format(
                visibility = self.visibility, style = self.style)
        else:
            return ''

    def __str__(self):
        # X name pin X Y length PinOrientation sizenum sizename part dmg type shape
        return 'X {name:s} {num:s} {at:s} {pin_length:d} {orientation:s} {sizenumber:d} {sizename:d} {unit_idx:d} {deMorgan_idx:d} {el_type:s}{shape}\n'.format(
            name = self.name, num = str(self.num),
            at = self.at, pin_length = self.pin_length, orientation = self.orientation,
            sizenumber = self.fontsize_pinnumber, sizename = self.fontsize_pinname,
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            el_type = self.el_type, shape = self.__pinShapeRender()
        )

    def translate(self, distance, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)
        obj.at.translate(distance)
        return obj

    def rotate(self, angle, origin = {'x':0, 'y':0}, rotate_pin_orientation = False,
            apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.rotate(angle = angle, origin = origin)
        if rotate_pin_orientation:
            raise NotImplementedError('Rotating the pin orientation is not yet implemented')
            #ToDo: Implement
            # set separate coordinate system to base of pin and calculate the rotation
            # needed around it. (can only be rotaded in steps of 90 degree)
            # determine new pin orientation and translate end point such that base point is
            # still at the same place.
        return obj

    def mirrorHorizontal(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        if obj.orientation is DrawingPin.PinOrientation.LEFT:
            obj.orientation = DrawingPin.PinOrientation.RIGHT
        elif obj.orientation is DrawingPin.PinOrientation.RIGHT:
            obj.orientation = DrawingPin.PinOrientation.LEFT
        obj.at.mirrorHorizontal()
        return obj

    def mirrorVertical(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        if obj.orientation is DrawingPin.PinOrientation.UP:
            obj.orientation = DrawingPin.PinOrientation.DOWN
        elif obj.orientation is DrawingPin.PinOrientation.DOWN:
            obj.orientation = DrawingPin.PinOrientation.UP
        obj.at.mirrorVertical()
        return obj

class DrawingRectangle:
    def __init__(self, start, end, **kwargs):
        self.start = Point(start)
        self.end = Point(end)
        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.line_width = int(kwargs.get('line_width', 10))

        fill = kwargs.get('fill', ElementFill.NO_FILL)
        if isinstance(fill, ElementFill):
            self.fill = fill
        else:
            raise TypeError('fill needs to be of type ElementFill')

    def __str__(self):
        # S X1 Y1 X2 Y2 part dmg pen fill
        return 'S {start:s} {end:s} {unit_idx:d} {deMorgan_idx:d} {line_width:d} {fill:s}\n'.format(
            start = self.start, end = self.end,
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            line_width = self.line_width, fill = self.fill
        )

    def toPolyline(self):
        p1 = Point(self.start)
        p3 = Point(self.end)
        p2 = Point(p1.x, p3.y)
        p4 = Point(p3.x, p1.y)

        points = [p1, p2, p3, p4, p1]

        polyline = DrawingPolyline(
            points=points,
            unit_idx=self.unit_idx, deMorgan_idx=self.deMorgan_idx,
            line_width=self.line_width, fill=self.fill
        )

        return polyline

    def translate(self, distance, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.start.translate(distance)
        obj.end.translate(distance)
        return obj

    def rotate(self, angle, origin = None, apply_on_copy = False):
        # obj = self if not apply_on_copy else deepcopy(self)
        if not apply_on_copy:
            raise NotImplementedError('Rotating the rectangles only implemented for copies -> converts to polyline')

        if origin is None:
            origin = Point((self.start.x + self.end.x)/2, (self.start.y + self.end.y)/2)

        obj = self.toPolyline()
        obj.rotate(angle, origin, False)
        return obj
        # return obj

    def mirrorVertical(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.start.mirrorVertical()
        obj.end.mirrorVertical()
        return obj

    def mirrorHorizontal(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.start.mirrorHorizontal()
        obj.end.mirrorHorizontal()
        return obj

class DrawingPolyline:
    def __init__(self, points, **kwargs):
        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.line_width = int(kwargs.get('line_width', 10))

        fill = kwargs.get('fill', ElementFill.NO_FILL)
        if isinstance(fill, ElementFill):
            self.fill = fill
        else:
            raise TypeError('fill needs to be of type ElementFill')

        if len(points) < 2:
            raise TypeError('A polyline needs at least two points')
        self.points=[]
        for point in points:
            self.points.append(Point(point))

    def __str__(self):
        # P count part dmg pen X Y ... fill
        return 'P {count:d} {unit_idx:d} {deMorgan_idx:d} {line_width} {points:s} {fill:s}\n'.format(
            count = len(self.points),
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            points = ' '.join(map(str, self.points)),
            fill = self.fill, line_width = self.line_width
        )

    def translate(self, distance, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        for point in obj.points:
            point.translate(distance)
        return obj

    def rotate(self, angle, origin = None, apply_on_copy = False):
        if origin is None:
            x = 0
            y = 0
            if self.points[0] == self.points[-1]:
                points = self.points[:-1]
            else:
                points = self.points

            for point in points:
                x += point.x
                y += point.y

            origin = Point(x/len(point), y/len(point))

        obj = self if not apply_on_copy else deepcopy(self)

        for point in obj.points:
            point.rotate(angle, origin)
        return obj

    def mirrorHorizontal(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        for point in obj.points:
            point.mirrorHorizontal()
        return obj

    def mirrorVertical(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        for point in obj.points:
            point.mirrorVertical()
        return obj

class DrawingArc:
    def __normalizeAngle(angle):
        angle = angle % 3600
        if angle > 1800:
            return angle - 3600
        if angle <= -1800:
            return 3600 + angle
        return angle

    def __ensureUniqueDrawing(self):
        if abs(self.angle_start - self.angle_end) == 1800:
            if self.angle_start > 0:
                self.angle_start -= 1
            else:
                self.angle_start += 1

            if self.angle_end > 0:
                self.angle_end -= 1
            else:
                self.angle_end += 1

    def __init__(self, at, radius, angle_start, angle_end, **kwargs):
        self.at = Point(at)
        self.radius = int(radius)
        self.angle_start = DrawingArc.__normalizeAngle(int(angle_start))
        self.angle_end = DrawingArc.__normalizeAngle(int(angle_end))
        self.__ensureUniqueDrawing()

        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.line_width = int(kwargs.get('line_width', 10))

        fill = kwargs.get('fill', ElementFill.NO_FILL)
        if isinstance(fill, ElementFill):
            self.fill = fill
        else:
            raise TypeError('fill needs to be of type ElementFill')

    def __str__(self):
        # A X Y radius start end part dmg pen fill Xstart Ystart Xend Yend
        start = Point(distance = self.radius, angle = self.angle_start/10).translate(self.at)
        end = Point(distance = self.radius, angle = self.angle_end/10).translate(self.at)
        return 'A {cp:s} {r:d} {angle_start:d} {angle_end:d} {unit_idx:d} {deMorgan_idx:d} {line_width:d} {fill:s} {p_start:s} {p_end:s}\n'.format(
            cp = self.at, r = self.radius,
            angle_start = self.angle_start, angle_end = self.angle_end,
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            fill = self.fill, line_width = self.line_width,
            p_start = start, p_end = end
        )

    def translate(self, distance, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.translate(distance)
        return obj

    def rotate(self, angle, origin = {'x':0, 'y':0}, apply_on_copy = False):
        # obj = self if not apply_on_copy else deepcopy(self)

        raise NotImplementedError('Rotating arcs is not yet implementd')
        # return obj

    def __mirrorAngleHorizontal(angle):
        if angle >= 0:
            return 1800 - angle
        return -1800 - angle

    def mirrorHorizontal(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)
        obj.at.mirrorHorizontal()
        obj.angle_start = DrawingArc.__mirrorAngleHorizontal(obj.angle_start)
        obj.angle_end = DrawingArc.__mirrorAngleHorizontal(obj.angle_end)
        return obj

    def mirrorVertical(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)
        obj.at.mirrorVertical()
        obj.angle_start *= -1
        obj.angle_end *= -1
        return obj

class DrawingCircle:
    def __init__(self, at, radius, **kwargs):
        self.at = Point(at)
        self.radius = int(radius)

        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.line_width = int(kwargs.get('line_width', 10))

        fill = kwargs.get('fill', ElementFill.NO_FILL)
        if isinstance(fill, ElementFill):
            self.fill = fill
        else:
            raise TypeError('fill needs to be of type ElementFill')

    def __str__(self):
        # C X Y radius part dmg pen fill
        return 'C {cp:s} {r:d} {unit_idx:d} {deMorgan_idx:d} {line_width:d} {fill:s}\n'.format(
            cp = self.at, r = self.radius,
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            fill = self.fill, line_width = self.line_width
        )

    def translate(self, distance, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.translate(distance)
        return obj

    def rotate(self, angle, origin = None, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)
        if origin is None:
            return obj

        obj.at.rotate(angle, origin)
        return obj

    def mirrorHorizontal(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.mirrorHorizontal()
        return obj

    def mirrorVertical(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.mirrorVertical()
        return obj

class DrawingText:
    class FontType(Enum):
        ITALIC = 'Italic'
        NORMAL = 'Normal'

        def __str__(self):
            return self.value

    class FontWeight(Enum):
        BOLD = '1'
        NORMAL = '0'

        def __str__(self):
            return self.value

    class VerticalAlignment(Enum):
        CENTER = 'C'
        TOP = 'T'
        BOTTOM ='B'

        def __str__(self):
            return self.value

    class HorizontalAlignment(Enum):
        CENTER = 'C'
        LEFT = 'L'
        RIGHT = 'R'

        def __str__(self):
            return self.value

    def __init__(self, at, text, **kwargs):
        self.at = at
        self.text = text
        self.angle = kwargs.get("angle", 0)
        self.size = int(kwargs.get("size", 50))

        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))

        self.hidden = int(kwargs.get('hidden', 0))
        if self.hidden not in [0,1]:
            raise TypeError('hidden needs to be 0 or 1')

        font_type = kwargs.get('font_type', DrawingText.FontType.NORMAL)
        if isinstance(font_type, DrawingText.FontType):
            self.font_type = font_type
        else:
            raise TypeError('font_type needs to be of type DrawingText.FontType')

        font_weight = kwargs.get('font_type', DrawingText.FontWeight.NORMAL)
        if isinstance(font_weight, DrawingText.FontWeight):
            self.font_weight = font_weight
        else:
            raise TypeError('font_weight needs to be of type DrawingText.FontWeight')

        valign = kwargs.get('valign', DrawingText.VerticalAlignment.CENTER)
        if isinstance(valign, DrawingText.VerticalAlignment):
            self.valign = valign
        else:
            raise TypeError('valign needs to be of type DrawingText.VerticalAlignment')

        halign = kwargs.get('halign', DrawingText.HorizontalAlignment.CENTER)
        if isinstance(halign, DrawingText.HorizontalAlignment):
            self.halign = halign
        else:
            raise TypeError('halign needs to be of type DrawingText.HorizontalAlignment')

    def __str__(self):
        # T angle X Y size hidden part dmg text italic bold Halign Valign
        return 'T {angle:d} {at:s} {size:d} {hidden:d} {unit_idx:d} {deMorgan_idx:d}'\
            ' "{text:s}" {italic:s} {bold:s} {Halign:s} {Valign:s}\n'.format(
                angle=int(self.angle*10), at=self.at, size=self.size,
                hidden=self.hidden, unit_idx=self.unit_idx, deMorgan_idx=self.deMorgan_idx,
                text=self.text, italic=self.font_type, bold=self.font_weight,
                Halign=self.halign, Valign=self.valign
            )

    def translate(self, distance, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.translate(distance)
        return obj

    def rotate(self, angle, origin = None, apply_on_copy = False):
        if origin is None:
            origin = self.at
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.rotate(angle, origin)
        obj.angle += angle
        return obj

    def mirrorHorizontal(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.mirrorHorizontal()
        return obj

    def mirrorVertical(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.at.mirrorVertical()
        return obj



class Drawing:
    def __init__(self):
        self.arc = []
        self.circle = []
        self.text = []
        self.rectangle = []
        self.polyline = []
        self.pins = []

    def __appendDrawing(self, drawing):
        for arc in drawing.arc:
            self.arc.append(arc)

        for circle in drawing.circle:
            self.circle.append(circle)

        for text in drawing.text:
            self.text.append(text)

        for rectangle in drawing.rectangle:
            self.rectangle.append(rectangle)

        for polyline in drawing.polyline:
            self.polyline.append(polyline)

        for pin in drawing.pins:
            self.pins.append(pin)

    def append(self, obj):
        if isinstance(obj, DrawingArc):
            self.arc.append(obj)
        elif isinstance(obj, DrawingCircle):
            self.circle.append(obj)
        elif isinstance(obj, DrawingText):
            self.text.append(obj)
        elif isinstance(obj, DrawingRectangle):
            self.rectangle.append(obj)
        elif isinstance(obj, DrawingPolyline):
            self.polyline.append(obj)
        elif isinstance(obj, DrawingPin):
            self.pins.append(obj)
        elif isinstance(obj, Drawing):
            self.__appendDrawing(obj)
        else:
            TypeError('trying to append an illegal type to Drawing. Maybe something is not yet implemented.')

    def __str__(self):
        drawing = 'DRAW\n'
        drawing += ''.join(sorted(map(str, self.arc)))
        drawing += ''.join(sorted(map(str, self.circle)))
        drawing += ''.join(sorted(map(str, self.text)))
        drawing += ''.join(sorted(map(str, self.rectangle)))
        drawing += ''.join(sorted(map(str, self.polyline)))
        drawing += ''.join(sorted(map(str, self.pins)))
        drawing += 'ENDDRAW\n'
        return drawing

    def mapOnAll(self, function, **kwargs):
        for element in self.arc:
            fp = getattr(element, function)
            fp(**kwargs)

        for element in self.circle:
            fp = getattr(element, function)
            fp(**kwargs)

        for element in self.text:
            fp = getattr(element, function)
            fp(**kwargs)

        for element in self.rectangle:
            fp = getattr(element, function)
            fp(**kwargs)

        for element in self.polyline:
            fp = getattr(element, function)
            fp(**kwargs)

        for element in self.pins:
            fp = getattr(element, function)
            fp(**kwargs)

    def translate(self, distance, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.mapOnAll('translate', distance=distance)
        return obj

    def rotate(self, angle, origin = {'x':0, 'y':0}, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.mapOnAll('rotate', angle = angle, origin = origin)
        return obj

    def mirrorHorizontal(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.mapOnAll('mirrorHorizontal')
        return obj

    def mirrorVertical(self, apply_on_copy = False):
        obj = self if not apply_on_copy else deepcopy(self)

        obj.mapOnAll('mirrorVertical')
        return obj

    def updatePinNumber(self, pinnumber_update_function=lambda x:x+1,
            pinname_update_function = lambda old_name, new_number: new_number):
        for pin in self.pins:
            pin.updatePinNumber(pinnumber_update_function, pinname_update_function)


class DrawingArray(Drawing):
    def __init__(self, original, distance, number_of_instances,
        pinnumber_update_function=lambda x:x+1,
        pinname_update_function = lambda old_name, new_number: new_number):
        Drawing.__init__(self)
        for i in range(number_of_instances):
            self.append(deepcopy(original))
            original.translate(distance)
            if isinstance(original, Drawing) or isinstance(original, DrawingPin):
                original.updatePinNumber(
                    pinnumber_update_function = pinnumber_update_function,
                    pinname_update_function = pinname_update_function)
