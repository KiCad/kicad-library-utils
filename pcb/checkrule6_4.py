# -*- coding: utf-8 -*-

def check_rule(module):
    bounds = module.padsBounds()
    lower = bounds[0]
    higher = bounds[1]

    x = lower[0] + higher[0]
    y = lower[1] + higher[1]

    if (x == 0.0 and y == 0.0):
        return ()

    return (x, y)

def fix_rule(module):
    dist = check_rule(module)
    if dist:
        module.setAnchor((dist[0]/2, dist[1]/2))
