# -*- coding: utf-8 -*-

def select_violating_pins(component):
    violating_pins = []
    for pin in component.pins:
        length = int(pin['length'])
        posx = int(pin['posx'])
        posy = int(pin['posy'])
        if (posx % 100) != 0 or (posy % 100) != 0:
            violating_pins.append(pin)
    return violating_pins

def check_rule(component):
    return select_violating_pins(component)
