#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from schlib import *

# cases covered by this script:
#  (1) pins with posx wrong if component has pins with L direction but not R direction
#  (2) pins with posx wrong if component has pins with R direction but not L direction
#  (3) pins with posy wrong if component has pins with U direction but not D direction
#  (4) pins with posy wrong if component has pins with D direction but not U direction
#  (5) pins with posx wrong if component has at least one pin wrong in each of the following direction: L, R
#  (6) pins with posy wrong if component has at least one pin wrong in each of the following direction: U, D
#  (7) tries to move the pin with L or R direction up or down keeping it 100mil away from another pin or of the rectangle symbol bounds
#  (8) tries to move the pin with U or D direction to left or right keeping it 100mil away from another pin or of the rectangle symbol bounds

def fix_component(component):
    pinsL = component.filterPins(direction='L')
    pinsL_count = len(pinsL)

    pinsR = component.filterPins(direction='R')
    pinsR_count = len(pinsR)

    pinsU = component.filterPins(direction='U')
    pinsU_count = len(pinsU)

    pinsD = component.filterPins(direction='D')
    pinsD_count = len(pinsD)

    print(component.name)

    # case (1)
    # assuming that all L pins have same length
    if pinsL_count > 0 and pinsR_count == 0:
        for pin in pinsL:
            posx = int(pin['posx'])
            length = int(pin['length'])
            old_posx = posx

            if ((posx % 100) != 0) and ((posx % 50) == 0):
                if length <= 100:
                    length += 50
                    posx += 50
                elif length >= 150:
                    length -= 50
                    posx -= 50

                pin['posx'] = str(posx)
                pin['length'] = str(length)
                print('  * fixing posx of %s: %i -> %i' % (pin['name'], old_posx, posx))

    # case (2)
    # assuming that all R pins have same length
    if pinsR_count > 0 and pinsL_count == 0:
        for pin in pinsR:
            posx = int(pin['posx'])
            length = int(pin['length'])
            old_posx = posx

            if ((posx % 100) != 0) and ((posx % 50) == 0):
                if length <= 100:
                    length += 50
                    posx -= 50
                elif length >= 150:
                    length -= 50
                    posx += 50

                pin['posx'] = str(posx)
                pin['length'] = str(length)
                print('  * fixing posx of %s: %i -> %i' % (pin['name'], old_posx, posx))

    # case (3)
    # assuming that all U pins have same length
    if pinsU_count > 0 and pinsD_count == 0:
        for pin in pinsU:
            posy = int(pin['posy'])
            length = int(pin['length'])
            old_posy = posy

            if ((posy % 100) != 0) and ((posy % 50) == 0):
                if length <= 100:
                    length += 50
                    posy -= 50
                elif length >= 150:
                    length -= 50
                    posy += 50

                pin['posy'] = str(posy)
                pin['length'] = str(length)
                print('  * fixing posy of %s: %i -> %i' % (pin['name'], old_posy, posy))

    # case (4)
    # assuming that all D pins have same length
    if pinsD_count > 0 and pinsU_count == 0:
        for pin in pinsD:
            posy = int(pin['posy'])
            length = int(pin['length'])
            old_posy = posy

            if ((posy % 100) != 0) and ((posy % 50) == 0):
                if length <= 100:
                    length += 50
                    posy += 50
                elif length >= 150:
                    length -= 50
                    posy -= 50

                pin['posy'] = str(posy)
                pin['length'] = str(length)
                print('  * fixing posy of %s: %i -> %i' % (pin['name'], old_posy, posy))

    # case (5)
    if pinsL_count > 0 and pinsR_count > 0:
        # check if at least one pin is wrong in L direction
        need_fix_L  = False
        for pin in pinsL:
            posx = int(pin['posx'])
            if ((posx % 100) != 0) and ((posx % 50) == 0):
                need_fix_L = True
                break

        # check if at least one pin is wrong in R direction
        need_fix_R  = False
        for pin in pinsR:
            posx = int(pin['posx'])
            if ((posx % 100) != 0) and ((posx % 50) == 0):
                need_fix_R = True
                break

        if need_fix_L and need_fix_R:
            for pin in (pinsL + pinsR):
                posx = int(pin['posx'])
                length = int(pin['length'])
                old_posx = posx

                if length <= 100:
                    length += 50
                    posx += 50 if posx > 0 else -50
                elif length >= 150:
                    length -= 50
                    posx += -50 if posx > 0 else 50

                pin['posx'] = str(posx)
                pin['length'] = str(length)
                print('  * fixing posx of %s: %i -> %i' % (pin['name'], old_posx, posx))

    # case (6)
    if pinsU_count > 0 and pinsD_count > 0:
        # check if at least one pin is wrong in L direction
        need_fix_U  = False
        for pin in pinsU:
            posy = int(pin['posy'])
            if ((posy % 100) != 0) and ((posy % 50) == 0):
                need_fix_U = True
                break

        # check if at least one pin is wrong in R direction
        need_fix_D  = False
        for pin in pinsD:
            posy = int(pin['posy'])
            if ((posy % 100) != 0) and ((posy % 50) == 0):
                need_fix_D = True
                break

        if need_fix_U and need_fix_D:
            for pin in (pinsU + pinsD):
                posy = int(pin['posy'])
                length = int(pin['length'])
                old_posy = posy

                if length <= 100:
                    length += 50
                    posy += 50 if posy > 0 else -50
                elif length >= 150:
                    length -= 50
                    posy += -50 if posy > 0 else 50

                pin['posy'] = str(posy)
                pin['length'] = str(length)
                print('  * fixing posy of %s: %i -> %i' % (pin['name'], old_posy, posy))

    # case (7)
    if len(component.draw['rectangles']) == 1:
        min_posy = int(component.draw['rectangles'][0]['endy'])
        max_posy = int(component.draw['rectangles'][0]['starty'])

        for d in ['L', 'R']:
            for n in range(2):
                pins = component.filterPins(direction=d)
                if n == 0:
                    pins = sorted(pins, key=lambda e: int(e['posy']))
                else:
                    pins = sorted(pins, key=lambda e: int(e['posy']), reverse=True)

                for i, pin in enumerate(pins):
                    posy = int(pin['posy'])
                    prev_posy = int(pins[i-1]['posy']) if i > 0 else None
                    next_posy = int(pins[i+1]['posy']) if i < (len(pins)-1) else None

                    if ((posy % 100) != 0) and ((posy % 50) == 0):
                        if abs((posy + 50) - max_posy) >= 100:
                            if next_posy == None or (next_posy != None and abs((posy + 50) - next_posy) >= 100):
                                pin['posy'] = str(posy + 50)
                                print('  * fixing posy of %s: %i -> %i' % (pin['name'], posy, posy+50))
                                continue

                        if abs((posy - 50) - min_posy) >= 100:
                            if prev_posy == None or (prev_posy != None and abs((posy - 50) - prev_posy) >= 100):
                                pin['posy'] = str(posy - 50)
                                print('  * fixing posy of %s: %i -> %i' % (pin['name'], posy, posy-50))
                                continue

    # case (8)
    if len(component.draw['rectangles']) == 1:
        min_posx = int(component.draw['rectangles'][0]['startx'])
        max_posx = int(component.draw['rectangles'][0]['endx'])

        for d in ['U', 'D']:
            for n in range(2):
                pins = component.filterPins(direction=d)
                if n == 0:
                    pins = sorted(pins, key=lambda e: int(e['posx']))
                else:
                    pins = sorted(pins, key=lambda e: int(e['posx']), reverse=True)

                for i, pin in enumerate(pins):
                    posx = int(pin['posx'])
                    prev_posx = int(pins[i-1]['posx']) if i > 0 else None
                    next_posx = int(pins[i+1]['posx']) if i < (len(pins)-1) else None

                    if ((posx % 100) != 0) and ((posx % 50) == 0):
                        if abs((posx + 50) - max_posx) >= 100:
                            if next_posx == None or (next_posx != None and abs((posx + 50) - next_posx) >= 100):
                                pin['posx'] = str(posx + 50)
                                print('  * fixing posx of %s: %i -> %i' % (pin['name'], posx, posx+50))
                                continue

                        if abs((posx - 50) - min_posx) >= 100:
                            if prev_posx == None or (prev_posx != None and abs((posx - 50) - prev_posx) >= 100):
                                pin['posx'] = str(posx - 50)
                                print('  * fixing posx of %s: %i -> %i' % (pin['name'], posx, posx-50))
                                continue

if len(sys.argv) < 2:
    print('Usage: %s <file1.lib> [file2.lib file3.lib file4.lib ...]' % sys.argv[0])
    exit(1)

for f in sys.argv[1:]:
    lib = SchLib(f)
    print('---', f, '---')
    for component in lib.components:
        fix_component(component)

    lib.save()
