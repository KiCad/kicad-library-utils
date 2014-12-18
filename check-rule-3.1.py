#!/usr/bin/env python
# -*- coding: utf-8 -*-

from schlib import *
import sys

show_pins = True

if len(sys.argv) < 2:
    print 'Usage: %s <file1.lib> [file2.lib file3.lib file4.lib ...]' % sys.argv[0]
    exit(1)

for f in sys.argv[1:]:
    lib = SchLib(f)

    for component in lib.components:
        header_ok = False
        for pin in component.pins:
            posx = int(pin['posx'])
            posy = int(pin['posy'])
            if ((posx % 100) != 0) and ((posy % 100) != 0):
                if not header_ok:
                    print 'library: %s, component: %s' % (f, component.name)
                    header_ok = True
                    if not show_pins: break

                print '   pin: %s (%s), dir: %s, posx: %s, posy: %s' % (pin['name'], pin['num'], pin['direction'], pin['posx'], pin['posy'])

            elif ((posx % 100) != 0):
                if not header_ok:
                    print 'library: %s, component: %s' % (f, component.name)
                    header_ok = True
                    if not show_pins: break

                print '   pin: %s (%s), dir: %s, posx: %s' % (pin['name'], pin['num'], pin['direction'], pin['posx'])

            elif ((posy % 100) != 0):
                if not header_ok:
                    print 'library: %s, component: %s' % (f, component.name)
                    header_ok = True
                    if not show_pins: break

                print '   pin: %s (%s), dir: %s, posy: %s' % (pin['name'], pin['num'], pin['direction'], pin['posy'])