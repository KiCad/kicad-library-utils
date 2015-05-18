# -*- coding: utf-8 -*-

# returns true if a violation is found
def check_rule(module):
    return not module.description

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    # Can't fix this one!
