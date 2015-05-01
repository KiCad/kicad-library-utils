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

def check_rule(component):
    violating_fields = select_violating_fields(component)
    violating_texts = select_violating_texts(component)
    violating_pins = select_violating_pins(component)
    return (violating_fields, violating_texts, violating_pins)
