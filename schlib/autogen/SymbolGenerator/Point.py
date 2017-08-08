import math

class Point():
    def __init__(self, coordinates=None, y=None, grid = None, distance = None, angle = None):
        if distance is not None and angle is not None:
            angle = math.radians(angle)
            self.x = int(distance*math.cos(angle))
            self.y = int(distance*math.sin(angle))
        elif coordinates is None:
            self.x = 0
            self.y = 0
        elif type(coordinates) in [int, float]:
            if y is not None:
                self.x = coordinates
                self.y = y
            else:
                raise TypeError('you have to give x and y coordinates')

        elif isinstance(coordinates, Point):
            self.x = coordinates.x
            self.y = coordinates.y

        elif type(coordinates) is dict:
            self.x = float(coordinates.get('x', 0))
            self.y = float(coordinates.get('y', 0))
        else:
            TypeError('unsuported type, Must be dict, point or coordinates given as number')

        self.grid = grid
        if grid is not None:
            self.roundToGrid()

    def rotate(self, angle, origin={'x':0, 'y':0}):
        op = Point(origin)

        angle = math.radians(angle)

        self.x = op.x + math.cos(angle) * (self.x - op.x) - math.sin(angle) * (self.y - op.y)
        self.y = op.y + math.sin(angle) * (self.x - op.x) + math.cos(angle) * (self.y - op.y)


    def translate(self, distance):
        dist = Point(distance)
        self.x += dist.x
        self.y += dist.y


    def mirrorHorizontal(self):
        self.x = -self.x

    def mirrorVertical(self):
        self.y = -self.y

    def roundCoordinateToGrid(value, base):
    	if value >= 0:
    		return math.floor(value/base) * base
    	return math.ceil(value/base) * base

    def roundToGrid(self, base=None):
        if base is None:
            base = self.grid

        if base is None:
            return

        self.x = Point.roundCoordinateToGrid(self.x, base)
        self.y = Point.roundCoordinateToGrid(self.y, base)

    def __repr__(self):
        return 'Point ({x:d}, {y:d})'.format(x = int(self.x), y = int(self.y))

    def __str__(self):
        return '{x:d} {y:d}'.format(x = int(self.x), y = int(self.y))

    def __format__(self, format):
        if format == 's':
            return str(self)
        elif format == 'r':
            return repr(self)
