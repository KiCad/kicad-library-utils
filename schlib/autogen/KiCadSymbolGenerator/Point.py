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
            self.x = int(round(distance*math.cos(angle)))
            self.y = int(round(distance*math.sin(angle)))
        elif coordinates is None:
            self.x = 0
            self.y = 0
        elif type(coordinates) in [int, float]:
            if y is not None:
                self.x = int(coordinates)
                self.y = int(y)
            else:
                raise TypeError('you have to give x and y coordinates')

        elif isinstance(coordinates, Point):
            self.x = coordinates.x
            self.y = coordinates.y

        elif type(coordinates) is dict:
            self.x = int(coordinates.get('x', 0))
            self.y = int(coordinates.get('y', 0))
        else:
            TypeError('unsuported type, Must be dict, point or coordinates given as number')

        self.grid = grid
        if grid is not None:
            self.roundToGrid()

    def rotate(self, angle, origin={'x':0, 'y':0}, **kwargs):
        point = self if not kwargs.get('apply_on_copy', False) else copy(self)
        point.grid = kwargs.get('new_grid', point.grid)

        op = Point(origin)

        angle = math.radians(angle)

        temp = int(op.x + math.cos(angle) * (point.x - op.x) - math.sin(angle) * (point.y - op.y))
        point.y = int(op.y + math.sin(angle) * (point.x - op.x) + math.cos(angle) * (point.y - op.y))
        point.x = temp

        if point.grid is not None:
            point.roundToGrid()
        return point


    def translate(self, distance, **kwargs):
        point = self if not kwargs.get('apply_on_copy', False) else copy(self)
        point.grid = kwargs.get('new_grid', point.grid)

        dist = Point(distance)
        point.x += dist.x
        point.y += dist.y
        if point.grid is not None:
            point.roundToGrid()
        return point


    def mirrorHorizontal(self, **kwargs):
        point = self if not kwargs.get('apply_on_copy', False) else copy(self)
        point.grid = kwargs.get('new_grid', point.grid)

        point.x = -point.x
        if point.grid is not None:
            point.roundToGrid()
        return point

    def mirrorVertical(self, **kwargs):
        point = self if not kwargs.get('apply_on_copy', False) else copy(self)
        point.grid = kwargs.get('new_grid', point.grid)

        point.y = -point.y
        if point.grid is not None:
            point.roundToGrid()
        return point

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

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Overrides the default implementation (unnecessary in Python 3)"""
        return not self.__eq__(other)
