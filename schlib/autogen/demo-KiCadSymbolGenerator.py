# File intented to demo some functions available in the Symbol Generator module.
# Another example is the connecor generator

# sys.path.append(os.path.join(sys.path[0],..)) # load KiCadSymbolGenerator path
# add KiCadSymbolGenerator to searchpath using export PYTHONPATH="${PYTHONPATH}<absolute path>/autogen/"
# or use relative module path. Example ..KiCadSymbolGenerator
from KiCadSymbolGenerator import *

generator = SymbolGenerator('demo')

current_symbol = generator.addSymbol('demo_sym1')
current_symbol.setReference('U', at={'x':0, 'y':150})
current_symbol.setValue(at={'x':0, 'y':-150})
current_symbol.drawing.append(DrawingPin(at=Point({'x':-210, 'y':0}, grid=100), number=0, orientation = DrawingPin.PinOrientation.RIGHT))

rect = DrawingRectangle(start={'x':-100, 'y':100}, end={'x':100, 'y':-100})

current_symbol.drawing.append(rect.rotate(45, apply_on_copy=True))
current_symbol.drawing.append(rect)

current_symbol.drawing.translate({'x':50, 'y':100})

testpoint = Point({})
testpoint2 = testpoint.translate(distance={'x':1,'y':1}, apply_on_copy=True) #apply on copy can be used to generate multiple equal parts.

generator.writeFiles()
