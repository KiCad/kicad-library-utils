# -*- coding: utf-8 -*-

# returns true if a violation is found
def check_rule(module):
    return (module.value['value'] != module.name or module.value['layer'] != 'F.Fab')

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    module.value['value'] = module.name
    module.value['layer'] = 'F.Fab'
