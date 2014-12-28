# -*- coding: utf-8 -*-

def select_violating_pins(component):
    violating_pins = []
    for pin in component.pins:
        length = int(pin['length'])
        if (length < 100) or (length - 100) % 50 != 0:
            violating_pins.append(pin)
    return violating_pins

def check_rule(component, component_printed=True):
    violating_pins = select_violating_pins(component)
    # If component violates rule
    if len(violating_pins) > 0:
        # If component header has not been already printed, print it
        if not component_printed:
            print '\tcomponent: %s' % component.name
            component_printed = True
        print '\tViolations of rule 3.2'
        for pin in violating_pins:
            print '\t\tpin: %s (%s), dir: %s, length: %s' % (pin['name'], pin['num'], pin['direction'], pin['length'])
    # Return status of component_printed
    return component_printed
