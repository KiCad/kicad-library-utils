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

def makeR_NET(file_lib, file_cmp, R):
    name="R_NET{0}".format(R)
    refdes="RN"
    file_cmp.write("#\n")
    file_cmp.write("$CMP "+name+"\n")
    file_cmp.write("D {0} Resistor network, star topology, bussed resistors, small symbol\n".format(R))
    file_cmp.write("K R Network star-topology\n")
    file_cmp.write("F http://www.vishay.com/docs/31509/csc.pdf\n")
    file_cmp.write("$ENDCMP\n")

    dp=100
    dot_diam=20
    pinlen=100
    R_len=160
    R_w=60
    W_dist=30
    box_l_offset=50
    left=-math.floor(R/2)*dp
    l_box=left-box_l_offset
    t_box=-125
    h_box=250
    w_box=(R-1)*dp+2*box_l_offset
    top=-200
    bottom=200
    
    file_lib.write("#\n")
    file_lib.write("# "+name+"\n")
    file_lib.write("#\n")
    file_lib.write("DEF "+name+" "+refdes+" 0 0 N N 1 F N\n")
    file_lib.write(("F0 \""+refdes+"\" {0} 0 50 V V C CNN\n").format(int(l_box-50)))
    file_lib.write(("F1 \""+name+"\" {0} 0 50 V V C CNN\n").format(int(l_box+w_box+50)))
    file_lib.write("F2 \"Resistors_ThroughHole:Resistor_Array_SIP{0}\" {1} 0 50 V I C CNN\n".format(R+1, int(l_box+w_box+50+75)))
    file_lib.write("F3 \"\" 0 0 50 H V C CNN\n")
    file_lib.write("$FPLIST\n")
    file_lib.write(" Resistor?Array?SIP*\n")
    file_lib.write("$ENDFPLIST\n")
    file_lib.write("DRAW\n")
    file_lib.write("S {0} {1} {2} {3} 0 1 10 f\n".format(int(l_box), int(t_box), int(l_box+w_box), int(t_box+h_box)))
    pinl=left
    y=top
    file_lib.write("X COM 1 {0} {1} {2} D 50 50 1 1 P\n".format(int(pinl), -int(top), int(pinlen)))
    file_lib.write("P 2 0 1 0 {0} {1} {0} {2} N\n".format(int(pinl), -int(top+pinlen), -int(bottom-pinlen-R_len)))
    for s in range(1,R+1):
        file_lib.write("X R{0} {1} {2} {3} {4} U 50 50 1 1 P\n".format(int(s), int(s+1), int(pinl), -int(bottom), int(pinlen)))
        file_lib.write("S {0} {1} {2} {3} 0 1 10 N\n".format(int(pinl-R_w/2), -int(bottom-pinlen-R_len), int(pinl+R_w/2), -int(bottom-pinlen)))
        if (s<R):
            file_lib.write("P 4 0 1 0 {0} {1} {0} {2} {3} {2} {3} {1} N\n".format(int(pinl), -int(bottom - pinlen - R_len), -int(bottom - pinlen - R_len - W_dist), int(pinl + dp)))
            file_lib.write("C {0} {1} 10 0 1 0 F\n".format(int(pinl), -int(bottom-pinlen-R_len-W_dist), int(dot_diam/2)))
        pinl=pinl+dp
    file_lib.write("ENDDRAW\n")
    file_lib.write("ENDDEF\n")


def makeR_NET_PAR_SIP(file_lib, file_cmp, R):
    name = "R_NET{0}_PAR_SIP".format(R)
    refdes = "RN"
    file_cmp.write("#\n")
    file_cmp.write("$CMP " + name + "\n")
    file_cmp.write("D {0} Resistor network, parallel topology, SIP package\n".format(R))
    file_cmp.write("K R Network parallel topology\n")
    file_cmp.write("F http://www.vishay.com/docs/31509/csc.pdf\n")
    file_cmp.write("$ENDCMP\n")
    
    dp = 100
    dR = 300
    pinlen = 150
    R_len = 160
    R_w = 60
    W_dist = 30
    box_l_offset = 50
    left = -roundG(((R - 1) * dR) / 2, 100)
    l_box = left - box_l_offset
    t_box = -75
    h_box = 250
    w_box = ((R - 1) * dR + dp) + 2 * box_l_offset
    top = -200
    bottom = 200
    
    file_lib.write("#\n")
    file_lib.write("# " + name + "\n")
    file_lib.write("#\n")
    file_lib.write("DEF " + name + " " + refdes + " 0 0 Y N 1 F N\n")
    file_lib.write(("F0 \"" + refdes + "\" {0} 0 50 V V C CNN\n").format(int(l_box - 50)))
    file_lib.write(("F1 \"" + name + "\" {0} 0 50 V V C CNN\n").format(int(l_box + w_box + 50)))
    file_lib.write("F2 \"Resistors_ThroughHole:Resistor_Array_SIP{0}\" {1} 0 50 V I C CNN\n".format(2 * R, int(
        l_box + w_box + 50 + 75)))
    file_lib.write("F3 \"\" 0 0 50 H V C CNN\n")
    file_lib.write("$FPLIST\n")
    file_lib.write(" Resistor?Array?SIP*\n")
    file_lib.write("$ENDFPLIST\n")
    file_lib.write("DRAW\n")
    file_lib.write(
        "S {0} {1} {2} {3} 0 1 10 f\n".format(int(l_box), int(t_box), int(l_box + w_box), int(t_box + h_box)))
    pinl = left
    y = top
    for s in range(1, R + 1):
        file_lib.write(
            "X R{0}.1 {1} {2} {3} {4} U 50 50 1 1 P\n".format(int(s), int(2 * s - 1), int(pinl), -int(bottom),
                                                              int(pinlen)))
        file_lib.write(
            "X R{0}.2 {1} {2} {3} {4} U 50 50 1 1 P\n".format(int(s), int(2 * s), int(pinl + dp), -int(bottom),
                                                              int(pinlen)))
        file_lib.write("S {0} {1} {2} {3} 0 1 10 N\n".format(int(pinl - R_w / 2), -int(bottom - pinlen - R_len),
                                                             int(pinl + R_w / 2), -int(bottom - pinlen)))
        file_lib.write("P 4 0 1 0 {0} {1} {0} {2} {3} {2} {3} {4} N\n".format(int(pinl), -int(bottom - pinlen - R_len),
                                                                              -int(bottom - pinlen - R_len - W_dist),
                                                                              int(pinl + dp), -int(bottom - pinlen)))
        pinl = pinl + dR
    file_lib.write("ENDDRAW\n")
    file_lib.write("ENDDEF\n")


def makeR_NET_PAR_DIP(file_lib, file_cmp, R):
    name = "R_NET{0}_PAR_DIP".format(R)
    namea = "R_PACK{0}".format(R)
    refdes = "RN"
    file_cmp.write("#\n")
    file_cmp.write("$CMP " + name + "\n")
    file_cmp.write("D {0} Resistor network, parallel topology, DIP package\n".format(R))
    file_cmp.write("K R Network parallel topology\n")
    file_cmp.write("$ENDCMP\n")
    file_cmp.write("#\n")
    file_cmp.write("$CMP " + namea + "\n")
    file_cmp.write("D {0} Resistor network, parallel topology, DIP package\n".format(R))
    file_cmp.write("K R Network parallel topology\n")
    file_cmp.write("$ENDCMP\n")

    dp = 100
    pinlen = 100
    R_len = 150
    R_w = 50
    W_dist = 30
    box_l_offset = 50
    box_t_offset = 20
    left = -roundG(((R - 1) * dp) / 2, 100)
    l_box = left - box_l_offset
    h_box = R_len+2*box_t_offset
    t_box = -h_box/2
    w_box = ((R - 1) * dp) + 2 * box_l_offset
    top = -200
    bottom = 200
    
    file_lib.write("#\n")
    file_lib.write("# " + name + "\n")
    file_lib.write("#\n")
    file_lib.write("DEF " + name + " " + refdes + " 0 0 Y N 1 F N\n")
    file_lib.write(("F0 \"" + refdes + "\" {0} 0 50 V V C CNN\n").format(int(l_box - 50)))
    file_lib.write(("F1 \"" + name + "\" {0} 0 50 V V C CNN\n").format(int(l_box + w_box + 50)))
    file_lib.write("F2 \"\" {0} 0 50 V I C CNN\n".format(int(
        l_box + w_box + 50 + 75)))
    file_lib.write("F3 \"\" 0 0 50 H V C CNN\n")
    file_lib.write("ALIAS "+namea+"\n")
    file_lib.write("$FPLIST\n")
    file_lib.write(" DIP*\n")
    file_lib.write(" SOIC*\n")
    file_lib.write("$ENDFPLIST\n")
    file_lib.write("DRAW\n")
    file_lib.write(
        "S {0} {1} {2} {3} 0 1 10 f\n".format(int(l_box), int(t_box), int(l_box + w_box), int(t_box + h_box)))
    pinl = left
    y = top
    for s in range(1, R + 1):
        file_lib.write("X R{0}.1 {1} {2} {3} {4} U 50 50 1 1 P\n".format(int(s), int(s), int(pinl), -int(bottom), int(pinlen)))
        file_lib.write("X R{0}.2 {1} {2} {3} {4} D 50 50 1 1 P\n".format(int(s), int(2*R-s+1), int(pinl), -int(top), int(pinlen)))
        file_lib.write("S {0} {1} {2} {3} 0 1 10 N\n".format(int(pinl - R_w / 2), -int(-R_len/2), int(pinl + R_w / 2), -int(R_len/2)))
        file_lib.write("P 2 0 1 0 {0} {1} {0} {2} N\n".format(int(pinl), -int(bottom - pinlen), -int(R_len/2)))
        file_lib.write("P 2 0 1 0 {0} {1} {0} {2} N\n".format(int(pinl), -int(-R_len/2), -int(top + pinlen)))
        pinl = pinl + dp
    file_lib.write("ENDDRAW\n")
    file_lib.write("ENDDEF\n")


def makeR_NET_DIV_SIP(file_lib, file_cmp, R):
    name = "R_NET{0}_DIV_SIP".format(R)
    refdes = "RN"
    file_cmp.write("#\n")
    file_cmp.write("$CMP " + name + "\n")
    file_cmp.write("D {0} Voltage Dividers network, Dual Terminator, SIP package\n".format(R))
    file_cmp.write("K R Network divider topology\n")
    file_cmp.write("F http://www.vishay.com/docs/31509/csc.pdf\n")
    file_cmp.write("$ENDCMP\n")

    dp = 200
    dot_diam = 20
    pinlen = 100
    R_len = 100
    R_w = 40
    W_dist = 30
    box_l_offset = 50
    left = -math.floor(R / 2) * dp
    top = -300
    bottom = 300
    l_box = left - box_l_offset
    t_box = top+pinlen
    h_box = abs(bottom-pinlen-t_box)
    w_box = (R-1) * dp +dp/2 + 2 * box_l_offset
    R_dist=(h_box-2*R_len)/3


    file_lib.write("#\n")
    file_lib.write("# " + name + "\n")
    file_lib.write("#\n")
    file_lib.write("DEF " + name + " " + refdes + " 0 0 Y N 1 F N\n")
    file_lib.write(("F0 \"" + refdes + "\" {0} 0 50 V V C CNN\n").format(int(l_box - 50)))
    file_lib.write(("F1 \"" + name + "\" {0} 0 50 V V C CNN\n").format(int(l_box + w_box + 50)))
    file_lib.write("F2 \"Resistors_ThroughHole:Resistor_Array_SIP{0}\" {1} 0 50 V I C CNN\n".format(R + 2, int(
        l_box + w_box + 50 + 75)))
    file_lib.write("F3 \"\" 0 0 50 H V C CNN\n")
    file_lib.write("$FPLIST\n")
    file_lib.write(" Resistor?Array?SIP*\n")
    file_lib.write("$ENDFPLIST\n")
    file_lib.write("DRAW\n")
    file_lib.write(
        "S {0} {1} {2} {3} 0 1 10 f\n".format(int(l_box), int(t_box), int(l_box + w_box), int(t_box + h_box)))
    pinl = left
    y = top
    file_lib.write("X COM1 1 {0} {1} {2} D 50 50 1 1 P\n".format(int(pinl), -int(top), int(pinlen)))
    file_lib.write("X COM2 {0} {1} {2} {3} D 50 50 1 1 P\n".format(int(R + 2), int(left+(R-1)*dp+dp/2), -int(top), int(pinlen)))
    file_lib.write("P 2 0 1 0 {0} {1} {0} {2} N\n".format(int(left+(R-1)*dp+dp/2), -int(bottom - pinlen - R_dist / 2), -int(top+pinlen)))
    
    for s in range(1, R + 1):
        file_lib.write("X R{0} {1} {2} {3} {4} U 50 50 1 1 P\n".format(int(s), int(s + 1), int(pinl), -int(bottom), int(pinlen)))
        
        file_lib.write("S {0} {1} {2} {3} 0 1 10 N\n".format(int(pinl - R_w / 2), -int(top+pinlen+R_dist), int(pinl + R_w / 2), -int(top+pinlen+R_dist+R_len)))
        file_lib.write("S {0} {1} {2} {3} 0 1 10 N\n".format(int(pinl + 3*R_w/2 - R_w / 2), -int(bottom-pinlen-R_dist), int(pinl + 3*R_w/2 + R_w / 2), -int(bottom-pinlen-R_dist-R_len)))
        file_lib.write("P 3 0 1 0 {0} {1} {0} {2} {3} {2} N\n".format(int(pinl+3*R_w/2), -int(bottom-pinlen-R_dist), -int(bottom-pinlen-R_dist/2), int(left+(R-1)*dp+dp/2)))
        if s==1:
            file_lib.write("P 2 0 1 0 {0} {1} {0} {2} N\n".format(int(pinl), -int(top + pinlen), -int(top + pinlen + R_dist)))
        if s>1:
            file_lib.write("P 3 0 1 0 {0} {1} {2} {1} {2} {3} N\n".format(int(pinl-dp), -int(top + pinlen+R_dist/2), int(pinl), -int(top + pinlen + R_dist)))
            

        file_lib.write("P 2 0 1 0 {0} {1} {0} {2} N\n".format(int(pinl), -int(bottom - pinlen), -int(top+pinlen+R_dist+R_len)))
        file_lib.write("P 3 0 1 0 {0} {1} {2} {1} {2} {3} N\n".format(int(pinl), -int(top+pinlen+R_dist+R_len+R_dist/2), int(pinl+3*R_w/2), -int(bottom-pinlen-R_dist-R_len)))
        file_lib.write("C {0} 0 {1} 0 1 0 F\n".format(int(pinl), int(dot_diam / 2)))
        if s>1: file_lib.write("C {0} {1} {2} 0 1 0 F\n".format(int(pinl+3*R_w/2), -int(bottom - pinlen - R_dist/2), int(dot_diam / 2)))
        if s<R: file_lib.write("C {0} {1} {2} 0 1 0 F\n".format(int(pinl), -int(top + pinlen + R_dist / 2),int(dot_diam / 2)))

        pinl = pinl + dp
    file_lib.write("ENDDRAW\n")
    file_lib.write("ENDDEF\n")
    
    
if __name__ == '__main__':
    file_lib = open("R_NET.lib", 'w')
    file_lib.write("EESchema-LIBRARY Version 2.3\n")
    file_lib.write("#encoding utf-8\n")

    file_cmp = open("R_NET.dcm", 'w')
    file_cmp.write("EESchema-DOCLIB  Version 2.0\n")
    for R in range(3, 14):
        makeR_NET(file_lib, file_cmp, R)
    for R in range(2,8):
        makeR_NET_PAR_SIP(file_lib, file_cmp, R)
    for R in [2,3,4,5,6,7,8,9,10,11]:
        makeR_NET_PAR_DIP(file_lib, file_cmp, R)
    for R in range(2,12):
        makeR_NET_DIV_SIP(file_lib, file_cmp, R)

    file_cmp.write("#End Doc Library\n")
    file_lib.write("#End Library\n")
