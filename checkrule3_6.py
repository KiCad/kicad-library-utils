# -*- coding: utf-8 -*-

def select_violating_fields(component):
    violating_fields = []
    for field in component.fields:
        text_size = int(field['text_size'])
        namekey = 'reference' if 'reference' in field else 'name'
        if (text_size != 50) and (field[namekey] != '""'):
            violating_fields.append(field)
    return violating_fields

def select_violating_texts(component):
    violating_texts = []
    for text in component.draw['texts']:
        text_size = int(text['text_size'])
        if text_size != 50:
            violating_texts.append(text)
    return violating_texts

def select_violating_pins(component):
    violating_pins = []
    for pin in component.pins:
        name_text_size = int(pin['name_text_size'])
        num_text_size = int(pin['num_text_size'])
        if (name_text_size != 50) or (num_text_size != 50):
            violating_pins.append(pin)
    return violating_pins

def check_rule(component, component_printed=True):
    violating_fields = select_violating_fields(component)
    violating_texts = select_violating_texts(component)
    violating_pins = select_violating_pins(component)
    # If component violates rule
    if (len(violating_fields) > 0) or (len(violating_texts) > 0) or (len(violating_pins) > 0):
        # If component header has not been already printed, print it
        if not component_printed:
            print '\tcomponent: %s' % component.name
            component_printed = True
        print '\tViolations of rule 3.6'
        for field in violating_fields:
            namekey = 'reference' if 'reference' in field else 'name'
            print '\t\tfield: %s, text_size: %s' % (field[namekey], field['text_size'])
        for text in violating_texts:
            print '\t\ttext: %s, text_size: %s' % (text['text'], text['text_size'])
        for pin in violating_pins:
            print '\t\tpin: %s (%s), dir: %s, name_text_size: %s, num_text_size: %s' % (pin['name'], pin['num'], pin['direction'], pin['name_text_size'], pin['num_text_size'])
    # Return status of component_printed
    return component_printed
