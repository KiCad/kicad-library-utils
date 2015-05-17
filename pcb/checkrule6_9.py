# -*- coding: utf-8 -*-

# returns true if a violation is found
def check_rule(module):
    if module.reference['font']['height'] != 1 or module.value['font']['height'] != 1:
       return True

    return False

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    module.reference['font']['height'] = 1
    module.value['font']['height'] = 1
