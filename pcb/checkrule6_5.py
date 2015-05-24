# -*- coding: utf-8 -*-

def check_rule(module):
    silk_lines = module.filterLines('F.SilkS')
    silk_lines += module.filterLines('B.SilkS')

    bad_width = []
    for line in silk_lines:
        # check the line width
        if line['width'] != 0.15:
            bad_width.append(line)

    if bad_width:
        return [bad_width]

    return []

def fix_rule(module):
    # first check if it's violating the rule
    lines = check_rule(module)
    if not lines: return

    # fix the line width
    for line in lines[0]:
        line['width'] = 0.15
