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

import math
from copy import copy

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

    def rotate(self, angle, origin={'x':0, 'y':0}, apply_on_copy = False):
        obj = self if not apply_on_copy else copy(self)

        op = Point(origin)

        angle = math.radians(angle)

        obj.x = op.x + math.cos(angle) * (obj.x - op.x) - math.sin(angle) * (obj.y - op.y)
        obj.y = op.y + math.sin(angle) * (obj.x - op.x) + math.cos(angle) * (obj.y - op.y)
        return obj


    def translate(self, distance, apply_on_copy = False):
        obj = self if not apply_on_copy else copy(self)

        dist = Point(distance)
        obj.x += dist.x
        obj.y += dist.y
        return obj


    def mirrorHorizontal(self, apply_on_copy = False):
        obj = self if not apply_on_copy else copy(self)

        obj.x = -obj.x
        return obj

    def mirrorVertical(self, apply_on_copy = False):
        obj = self if not apply_on_copy else copy(self)

        obj.y = -obj.y
        return obj

    def roundCoordinateToGrid(value, base, apply_on_copy = False):
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
