# -*- coding: utf-8 -*-

# returns non zero if a violation is found
def check_rule(module):
    return module.tags.count(',')

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    module.tags = ' '.join(module.tags.replace(' ', '').split(','))
