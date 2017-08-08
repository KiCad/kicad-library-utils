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
            return

        elif type(coordinates) is dict:
            self.x = float(coordinates.get('x', 0))
            self.y = float(coordinates.get('y', 0))
        else:
            TypeError('unsuported type, Must be dict, point or coordinates given as number')

        self.grid = grid
        if grid is not None:
            self.roundToGrid()

    def __operatorPreperation(self, obj):
        other_point = None
        if type(obj) in [int, float]:
            other_point = Point(obj, obj)
        else:
            other_point = Point(obj)
        grid = self.grid
        if other_point.grid is not None:
            if grid is None:
                grid = other_point.grid
            else:
                if other_point.grid > grid:
                    grid = other_point.grid

        return other_point, grid

    def __add__(self, obj):
        other_point, grid = self.__operatorPreperation(obj)
        return Point({'x': self.x + other_point.x,
                      'y': self.y + other_point.y}, grid = grid)

    def __sub__(self, obj):
        other_point, grid = self.__operatorPreperation(obj)
        return Point({'x': self.x - other_point.x,
                      'y': self.y - other_point.y}, grid = grid)

    def rotate(self, angle, origin={'x':0, 'y':0}):
        op = Point(origin)
        temp = self-op

        angle = math.radians(angle)

        temp.x = math.cos(angle) * temp.x - math.sin(angle) * temp.y
        temp.y = math.sin(angle) * temp.x + math.cos(angle) * temp.y
        return temp + op

    def translate(self, distance):
        dist = Point(distance)
        self += dist

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
