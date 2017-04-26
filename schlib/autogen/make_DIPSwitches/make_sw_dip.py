#!/usr/bin/env python

import sys
import os
import math


def roundG(x, g):
    if (x>0):
        return math.ceil(x/g)*g
    else:
        return math.floor(x/g)*g


def roundCrt(x):
    return roundG(x, 0.05)

def makeSW_DIP(file_lib, file_cmp, switches):
    file_cmp.write("#\n")
    file_cmp.write("$CMP SW_DIP{0}\n".format(switches))
    file_cmp.write("D {0}x DIP Switch, Single Pole Single Throw (SPST) switch, small symbol\n".format(switches))
    file_cmp.write("K dip switch\n")
    file_cmp.write("$ENDCMP\n")

    dp=100
    circdiam=20
    pinlen=200
    sw_len=200
    w_box=300
    lever_angle=15
    lever_len=sw_len-circdiam
    w=sw_len+2*pinlen
    left=-w/2
    l_box=-w_box/2
    top=-round(switches/2)*dp
    h=pins*dp
    h_box=h+dp
    t_box=top-dp
    file_lib.write("#\n")
    file_lib.write("# SW_DIP{0}\n".format(switches))
    file_lib.write("#\n")
    file_lib.write("DEF SW_DIP{0} SW 0 0 Y N 1 F N\n".format(int(switches)))
    file_lib.write("F0 \"SW\" 0 {0} 50 H V C CNN\n".format(-int(t_box-50)))
    file_lib.write("F1 \"SW_DIP{0}\" 0 {1} 50 H V C CNN\n".format(switches, -int(t_box+h_box+50)))
    file_lib.write("F2 \"\" 0 0 50 H V C CNN\n")
    file_lib.write("F3 \"\" 0 0 50 H V C CNN\n")
    file_lib.write("$FPLIST\n")
    file_lib.write(" SW?DIP?x{0}*\n".format(switches))
    file_lib.write("$ENDFPLIST\n")
    file_lib.write("DRAW\n")
    file_lib.write("S {0} {1} {2} {3} 0 1 10 f\n".format(int(l_box), -int(t_box), int(l_box+w_box), -int(t_box+h_box)))
    pinl=1
    pinr=2*switches
    y=top
    for s in range(1,switches+1):
        file_lib.write("X ~ {0} {1} {2} {3} R 50 50 1 1 I\n".format(int(pinl), int(left), -int(y), int(pinlen)))
        file_lib.write("X ~ {0} {1} {2} {3} L 50 50 1 1 I\n".format(int(pinr), int(left+w), -int(y), int(pinlen)))
        file_lib.write("C {0} {1} {2} 0 0 0 N\n".format(-int(sw_len/2-circdiam), -int(y), int(circdiam)))
        file_lib.write("C {0} {1} {2} 0 0 0 N\n".format(int(sw_len/2-circdiam), -int(y), int(circdiam)))
        file_lib.write("P 2 0 0 0 {0} {2} {1} {3} N\n".format(int(-(sw_len/2-circdiam)+(circdiam)*math.cos(lever_angle/180*3.1415)), int(-(sw_len/2-circdiam)+lever_len*math.cos(lever_angle/180*3.1415)), -int(y-circdiam*math.sin(lever_angle/180*3.1415)), -int(y-lever_len*math.sin(lever_angle/180*3.1415))))

        pinl=pinl+1
        pinr=pinr-1
        y=y+dp
    file_lib.write("ENDDRAW\n")
    file_lib.write("ENDDEF\n")



def makeSW_DIP_ALT(file_lib, file_cmp, switches):
    file_cmp.write("#\n")
    file_cmp.write("$CMP SW_DIP{0}_ALT\n".format(switches))
    file_cmp.write("D {0}x DIP Switch, Single Pole Single Throw (SPST) switch, small symbol, alternative symbol\n".format(switches))
    file_cmp.write("K dip switch\n")
    file_cmp.write("$ENDCMP\n")

    dp=100
    swh=25
    pinlen=200
    sw_len=200
    w_box=300
    w=sw_len+2*pinlen
    left=-w/2
    l_box=-w_box/2
    top=-round(switches/2)*dp
    h=pins*dp
    h_box=h+dp
    t_box=top-dp
    file_lib.write("#\n")
    file_lib.write("# SW_DIP{0}_ALT\n".format(switches))
    file_lib.write("#\n")
    file_lib.write("DEF SW_DIP{0}_ALT SW 0 0 Y N 1 F N\n".format(int(switches)))
    file_lib.write("F0 \"SW\" 0 {0} 50 H V C CNN\n".format(-int(t_box-50)))
    file_lib.write("F1 \"SW_DIP{0}_ALT\" 0 {1} 50 H V C CNN\n".format(switches, -int(t_box+h_box+50)))
    file_lib.write("F2 \"\" 0 0 50 H V C CNN\n")
    file_lib.write("F3 \"\" 0 0 50 H V C CNN\n")
    file_lib.write("$FPLIST\n")
    file_lib.write(" SW?DIP?x{0}*\n".format(switches))
    file_lib.write("$ENDFPLIST\n")
    file_lib.write("DRAW\n")
    file_lib.write("S {0} {1} {2} {3} 0 1 10 f\n".format(int(l_box), -int(t_box), int(l_box+w_box), -int(t_box+h_box)))
    pinl=1
    pinr=2*switches
    y=top
    for s in range(1,switches+1):
        file_lib.write("X ~ {0} {1} {2} {3} R 50 50 1 1 I\n".format(int(pinl), int(left), -int(y), int(pinlen)))
        file_lib.write("X ~ {0} {1} {2} {3} L 50 50 1 1 I\n".format(int(pinr), int(left+w), -int(y), int(pinlen)))
        file_lib.write("S {0} {2} {1} {3} 0 1 0 F\n".format(int(-sw_len/2), 0, -int(y-swh), -int(y+swh)))
        file_lib.write("S {0} {2} {1} {3} 0 1 0 N\n".format(int(-sw_len/2), int(sw_len/2), -int(y-swh), -int(y+swh)))

        pinl=pinl+1
        pinr=pinr-1
        y=y+dp
    file_lib.write("ENDDRAW\n")
    file_lib.write("ENDDEF\n")


if __name__ == '__main__':
    file_lib = open("sw_dip.lib", 'w')
    file_lib.write("EESchema-LIBRARY Version 2.3\n")
    file_lib.write("#encoding utf-8\n")

    file_cmp = open("sw_dip.cmp", 'w')
    file_cmp.write("EESchema-DOCLIB  Version 2.0\n")
    for pins in range(1, 13):
        makeSW_DIP(file_lib, file_cmp, pins)
    for pins in range(1, 13):
        makeSW_DIP_ALT(file_lib, file_cmp, pins)

    file_cmp.write("#End Doc Library\n")
    file_lib.write("#End Library\n")
