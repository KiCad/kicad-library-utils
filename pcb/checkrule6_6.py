# -*- coding: utf-8 -*-

# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

# returns the problematic lines where the violation is found
def check_rule(module):
    courtyard_lines = module.filterLines('F.CrtYd')
    courtyard_lines += module.filterLines('B.CrtYd')

    bad_width = []
    bad_courtyard = []
    for line in courtyard_lines:
        # check the line width
        if line['width'] != 0.05:
            bad_width.append(line)

        # check if there is proper rounding 0.05 of courtyard lines

        # convert position to nanometers (add/subtract 1/10^7 to avoid wrong rounding and cast to int)
        # int pos_x = (d_pos_x + ((d_pos_x >= 0) ? 0.0000001 : -0.0000001)) * 1000000;
        # int pos_y = (d_pos_y + ((d_pos_y >= 0) ? 0.0000001 : -0.0000001)) * 1000000;
        x, y = line['start']['x'], line['start']['y']
        x = int( (x + (0.0000001 if x >= 0 else -0.0000001))*1E6 )
        y = int( (y + (0.0000001 if y >= 0 else -0.0000001))*1E6 )
        start_is_wrong = (x % 0.05E6) or (y % 0.05E6)

        x, y = line['end']['x'], line['end']['y']
        x = int( (x + (0.0000001 if x >= 0 else -0.0000001))*1E6 )
        y = int( (y + (0.0000001 if y >= 0 else -0.0000001))*1E6 )
        end_is_wrong = (x % 0.05E6) or (y % 0.05E6)

        if start_is_wrong or end_is_wrong:
            bad_courtyard.append(line)

    if bad_width or bad_courtyard:
        return [bad_width, bad_courtyard]

    return []

def fix_rule(module):
    # first check if it's violating the rule
    lines = check_rule(module)
    if not lines: return

    # fix the line width
    for line in lines[0]:
        line['width'] = 0.05

    # fix the courtyard
    # TODO
