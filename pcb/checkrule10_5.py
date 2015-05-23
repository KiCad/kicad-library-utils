# -*- coding: utf-8 -*-

def check_rule(module):
    pth_count = len(module.filterPads('thru_hole'))
    smd_count = len(module.filterPads('smd'))

    if ((pth_count > smd_count and module.attribute != 'pth') or
        (smd_count > pth_count and module.attribute != 'smd')):
        return {'pth':pth_count, 'smd':smd_count}

    return {}

def fix_rule(module):
    count = check_rule(module)
    if count:
        if count['pth'] > count['smd']:
            module.attribute = 'pth'
        elif count['smd'] > count['pth']:
            module.attribute = 'smd'
