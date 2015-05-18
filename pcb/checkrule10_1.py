# -*- coding: utf-8 -*-

import os

# returns true if a violation is found
def check_rule(module):
    return os.path.splitext(os.path.basename(module.filename))[0] != module.name

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    module.name = os.path.splitext(os.path.basename(module.filename))[0]