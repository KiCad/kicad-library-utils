# https://www.compuphase.com/electronics/LibraryFileFormats.pdf

from enum import Enum
from Point import Point

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
        self.num = str(number)
        self.name = str(kwargs.get('name', self.num))
        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.pin_lenght = int(kwargs.get('pin_lenght', 100))
        self.fontsize_pinnumber = int(kwargs.get('sizenumber', 50))
        self.fontsize_pinname = int(kwargs.get('sizename', self.fontsize_pinnumber))

        el_type = kwargs.get('el_type', DrawingPin.PinElectricalType.EL_TYPE_PASSIVE)
        if isinstance(el_type, DrawingPin.PinElectricalType):
            self.el_type = el_type
        else:
            raise TypeError('el_type needs to be of type PinElectricalType')

        visiblility = kwargs.get('visiblility', DrawingPin.PinVisibility.VISIBLE)
        if isinstance(visiblility, DrawingPin.PinVisibility):
            self.visiblility = visiblility
        else:
            raise TypeError('visiblility needs to be of type PinVisibility')

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

    def __pinShapeRender(self):
        if self.visiblility is DrawingPin.PinVisibility.INVISIBLE or self.style is not DrawingPin.PinStyle.SHAPE_LINE:
            return ' {visiblility:s}{style:s}'.format(
                visiblility = self.visiblility, style = self.style)
        else:
            return ''

    def __str__(self):
        # X name pin X Y length PinOrientation sizenum sizename part dmg type shape
        return 'X {name:s} {num:s} {at:s} {pin_length:d} {orientation:s} {sizenumber:d} {sizename:d} {unit_idx:d} {deMorgan_idx:d} {el_type:s}{shape}\n'.format(
            name = self.name, num = self.num,
            at = self.at, pin_length = self.pin_lenght, orientation = self.orientation,
            sizenumber = self.fontsize_pinnumber, sizename = self.fontsize_pinname,
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            el_type = self.el_type, shape = self.__pinShapeRender()
        )

class DrawingRectangle:
    def __init__(self, start, end, **kwargs):
        self.start = Point(start)
        self.end = Point(end)
        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.line_width = int(kwargs.get('line_width', 10))

        fill = kwargs.get('fill', ElementFill.FILL_BACKGROUND)
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

class DrawingPolyline:
    def __init__(self, points, **kwargs):
        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.line_width = int(kwargs.get('line_width', 10))

        fill = kwargs.get('fill', ElementFill.FILL_BACKGROUND)
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
        return 'P {count:d} {unit_idx:d} {deMorgan_idx:d} {points:s} {fill:s}\n'.format(
            count = len(self.points),
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            points = ' '.join(map(str, self.points)),
            fill = self.fill
        )

class DrawingArc:
    def __init__(self, center, radius, angle_start, angle_end, **kwargs):
        self.center = Point(center)
        self.radius = int(radius)
        self.angle_start = int(angle_start)
        self.angle_end = int(angle_end)

        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.line_width = int(kwargs.get('line_width', 10))

        fill = kwargs.get('fill', ElementFill.FILL_BACKGROUND)
        if isinstance(fill, ElementFill):
            self.fill = fill
        else:
            raise TypeError('fill needs to be of type ElementFill')

    def __str__(self):
        # A X Y radius start end part dmg pen fill Xstart Ystart Xend Yend
        start = Point(distance = self.radius, angle = self.angle_start/10)
        end = Point(distance = self.radius, angle = self.angle_end/10)
        return 'A {cp:s} {r:d} {angle_start:d} {angle_end:d} {unit_idx:d} {deMorgan_idx:d} {line_width:d} {fill:s} {p_start:s} {p_end:s}\n'.format(
            cp = self.center, r = self.radius,
            angle_start = self.angle_start, angle_end = self.angle_end,
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            fill = self.fill,
            p_start = start, p_end = end
        )

class DrawingCircle:
    def __init__(self, center, radius, **kwargs):
        self.center = Point(center)
        self.radius = int(radius)

        self.unit_idx = int(kwargs.get('unit_idx', 1))
        self.deMorgan_idx = int(kwargs.get('deMorgan_idx', 1))
        self.line_width = int(kwargs.get('line_width', 10))

        fill = kwargs.get('fill', ElementFill.FILL_BACKGROUND)
        if isinstance(fill, ElementFill):
            self.fill = fill
        else:
            raise TypeError('fill needs to be of type ElementFill')

    def __str__(self):
        # C X Y radius part dmg pen fill
        return 'C {cp:s} {r:d} {unit_idx:d} {deMorgan_idx:d} {line_width:d} {fill:s}\n'.format(
            cp = self.center, r = self.radius,
            unit_idx = self.unit_idx, deMorgan_idx = self.deMorgan_idx,
            fill = self.fill
        )

class Drawing:
    def __init__(self):
        self.rectangle = []
        self.polyline = []
        self.arc = []
        self.pins = []
        self.circle = []

    def append(self, obj):
        if isinstance(obj, DrawingPin):
            self.pins.append(obj)
        elif isinstance(obj, DrawingRectangle):
            self.rectangle.append(obj)
        elif isinstance(obj, DrawingPolyline):
            self.polyline.append(obj)
        elif isinstance(obj, DrawingArc):
            self.arc.append(obj)
        elif isinstance(obj, DrawingCircle):
            self.circle.append(obj)
        else:
            TypeError('trying to append an illegal type to Drawing. Maybe something is not yet implemented.')

    def __str__(self):
        drawing = 'DRAW\n'
        drawing += ''.join(map(str, self.arc))
        drawing += ''.join(map(str, self.circle))
        drawing += ''.join(map(str, self.rectangle))
        drawing += ''.join(map(str, self.polyline))
        drawing += ''.join(map(str, self.pins))
        drawing += 'ENDDRAW\n'
        return drawing

if __name__ == '__main__':
    drawing = Drawing()
    drawing.append(DrawingPin(num=1))
    print(drawing)
