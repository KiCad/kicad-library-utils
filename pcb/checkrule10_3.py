# -*- coding: utf-8 -*-

# returns non zero if a violation is found
def check_rule(module):
    if module.tags:
        return module.tags.count(',')

    return 0

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    module.tags = ' '.join(module.tags.replace(' ', '').split(','))
