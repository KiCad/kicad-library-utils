# -*- coding: utf-8 -*-

def select_violating_pins(component):
    violating_pins = []
    for pin in component.pins:
        length = int(pin['length'])
        if length == 0: continue
        if (length < 100) or (length - 100) % 50 != 0:
            violating_pins.append(pin)
    return violating_pins

def check_rule(component):
    return select_violating_pins(component)
