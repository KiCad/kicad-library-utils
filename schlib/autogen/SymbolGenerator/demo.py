from SymbolGenerator import *
from Point import Point
from DrawingElements import *

generator = SymbolGenerator('demo')

current_symbol = generator.addSymbol('demo_sym1')
current_symbol.setReference('U', at={'x':0, 'y':150})
current_symbol.setValue(at={'x':0, 'y':-150})
current_symbol.drawing.append(DrawingPin(at=Point({'x':-210, 'y':0}, grid=100), number=0, orientation = DrawingPin.PinOrientation.RIGHT))
current_symbol.drawing.append(DrawingRectangle(start={'x':-100, 'y':100}, end={'x':100, 'y':-100}))
current_symbol.drawing.translate({'x':50, 'y':100})
generator.writeFiles()
