#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math

class BoundingBox(object):
    
    xmin = None
    ymin = None
    xmax = None
    ymax = None

    def __init__(self, xmin=None, ymin=None, xmax=None, ymax=None):
        self.addPoint(xmin, ymin)
        self.addPoint(xmax, ymax)
        
    def checkMin(self, current, compare):
        if current == None:
            return compare
            
        if compare == None:
            return current
        
        if compare < current:
            return compare
            
        return current
        
    def checkMax(self, current, compare):
        if current == None:
            return compare
            
        if compare == None:
            return current
            
        if compare > current:
            return compare
            
        return current
        
    def addPoint(self, x, y, radius=0):
        # x might be 'None' so prevent subtraction 
        self.xmin = self.checkMin(self.xmin, x - radius if x else x)
        self.xmax = self.checkMax(self.xmax, x + radius if x else x)
        
        # y might be 'None' so prevent subtraction
        self.ymin = self.checkMin(self.ymin, y - radius if y else y)
        self.ymax = self.checkMax(self.ymax, y + radius if y else y)
        
    def addBoundingBox(self, other):
        self.addPoint(other.xmin, other.ymin)
        self.addPoint(other.xmax, other.ymax)
        
    @property
    def valid(self):
        if not self.xmin or not self.ymin or not self.xmax or not self.ymax:
            return False

        return True
        
    def containsPoint(self, x, y):
        if not self.valid:
            return False
            
        if x < self.xmin or self.xmax < x:
            return False
            
        if y < self.ymin or self.ymax < y:
            return False
            
        return True
        
    def expand(self, distance):
        if not self.valid:
            return
        self.xmin -= distance
        self.ymin -= distance
        
        self.xmax += distance
        self.ymax += distance
        
    def overlaps(self, other):
        return any([
            self.containsPoint(other.xmin, other.ymin),
            self.containsPoint(other.xmin, other.ymax),
            self.containsPoint(other.xmax, other.ymax),
            self.containsPoint(other.xmax, other.ymin)
            ])
            
    @property
    def x(self):
        return self.xmin
        
    @property
    def y(self):
        return self.ymin
            
    @property
    def width(self):
        if not self.xmin or not self.xmax:
            return 0
        return self.xmax - self.xmin
        
    @property
    def height(self):
        if not self.ymin or not self.ymax:
            return 0
        return self.ymax - self.ymin
        
    @property
    def size(self):
        return {'x': self.width, 'y': self.height}
        
    @property
    def center(self):
        return {'x': self.xmin + self.width / 2, 'y': self.ymin + self.height/2 }
            
if __name__ == '__main__':
    bb1 = BoundingBox(-20,50,10,-20)
    bb2 = BoundingBox(-5,-5,7,21)
    
    bb3 = BoundingBox(2,200)
    bb3.addPoint(3,5)
    
    bb3.addBoundingBox(bb1)
    
    print(bb1.size)
    print(bb2.size)
    print(bb3.size)
            