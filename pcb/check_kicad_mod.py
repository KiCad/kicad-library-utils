#!/usr/bin/env python

from __future__ import print_function

import argparse
from kicad_mod import *
import sys, os
# point to the correct location for the print_color script
sys.path.append(os.path.join(sys.path[0], '..', 'schlib'))

from print_color import *
from rules import *

# enable windows wildcards
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument('kicad_mod_files', nargs='+')
parser.add_argument('--fix', help='fix the violations if possible', action='store_true')
parser.add_argument('--fixmore', help='fix additional violations, not covered by --fix (e.g. rectangular courtyards), implies --fix!', action='store_true')
parser.add_argument('--addsilkscreenrect', help='adds a rectangle around the component on the silkscreen-layer', action='store_true')
parser.add_argument('--rotate', help='rotate the whole symbol by the given number of degrees', action='store', default=0)
parser.add_argument('--nocolor', help='does not use colors to show the output', action='store_true')
parser.add_argument('-v', '--verbose', help='show status of all modules and extra information about the violation', action='store_true')
parser.add_argument('-s', '--silent', help='skip output for symbols passing all checks', action='store_true')

args = parser.parse_args()
if args.fixmore:
    args.fix=True

printer = PrintColor(use_color=not args.nocolor)

exit_code = 0

# get all rules
all_rules = []
for f in dir():
    if f.startswith('rule'):
        all_rules.append(globals()[f].Rule)

files = []

for f in args.kicad_mod_files:
    files += glob(f)

for filename in files:
    try:
        module = KicadMod(filename)
    except:
        printer.red('could not parse module: %s' % filename)
        exit_code += 1
        continue

    if args.rotate!=0:
        module.rotateFootprint(int(args.rotate))
        printer.green('rotated footprint by {deg} degrees'.format(deg=int(args.rotate)))
        
    n_violations = 0
    for rule in all_rules:
        rule = rule(module,args)
        if rule.check():
            #this is the first violation
            if n_violations == 0:
                printer.green('checking module: %s' % module.name)
            n_violations += 1
            printer.yellow('Violating ' + rule.name, indentation=2)
            if args.verbose:
                printer.light_blue(rule.description, indentation=4, max_width=100)
                if len(rule.verbose_message)>0:
                    vm=rule.verbose_message.split('\n');
                    for v in vm:
                        printer.blue(v, indentation=6, max_width=100)

                # example of customized printing feedback by checking the rule name
                # and a specific variable of the rule
                #if rule.name == 'Rule 6.6' and len(rule.f_courtyard_all) == 0:
                #    printer.red('No courtyard line found in the module', indentation=4)
        if args.fix:
            rule.fix()
            if args.verbose:
                if len(rule.fix_verbose_message)>0:
                    vm=rule.fix_verbose_message.split('\n');
                    for v in vm:
                        printer.red(v, indentation=8, max_width=100)

    if args.addsilkscreenrect:
        # create courtyard if does not exists
        overpadBounds=module.overpadsBounds()
        geoBounds=module.geometricBounds('F.Fab')
        b={'lower':{'x':1.0E99, 'y':1.0E99},'higher':{'x':-1.0E99, 'y':-1.0E99}}
        if (geoBounds['lower']['x']>1.0E98 and geoBounds['lower']['x']==geoBounds['lower']['y']) or (geoBounds['higher']['x']<-1.0e98 and geoBounds['higher']['x']==geoBounds['higher']['y']):
            geoBounds=module.geometricBounds('B.Fab')               
        if (geoBounds['lower']['x']>1.0E98 and geoBounds['lower']['x']==geoBounds['lower']['y']) or (geoBounds['higher']['x']<-1.0e98 and geoBounds['higher']['x']==geoBounds['higher']['y']):
            geoBounds=module.geometricBounds('F.SilkS')
        if (geoBounds['lower']['x']>1.0E98 and geoBounds['lower']['x']==geoBounds['lower']['y']) or (geoBounds['higher']['x']<-1.0e98 and geoBounds['higher']['x']==geoBounds['higher']['y']):
            geoBounds=module.geometricBounds('B.SilkS')
        
        b['lower']['x']=min(b['lower']['x'],overpadBounds['lower']['x'])
        b['lower']['y']=min(b['lower']['y'],overpadBounds['lower']['y'])
        b['higher']['x']=max(b['higher']['x'],overpadBounds['higher']['x'])
        b['higher']['y']=max(b['higher']['y'],overpadBounds['higher']['y'])
        b['lower']['x']=min(b['lower']['x'],geoBounds['lower']['x'])
        b['lower']['y']=min(b['lower']['y'],geoBounds['lower']['y'])
        b['higher']['x']=max(b['higher']['x'],geoBounds['higher']['x'])
        b['higher']['y']=max(b['higher']['y'],geoBounds['higher']['y'])
        
        #print('b=',b)
        if b['higher']['x']!=b['lower']['x'] and b['higher']['y']!=b['lower']['y'] and b['higher']['x']>-1.0E99 and b['higher']['y']>-1.0E99 and b['lower']['x']<1.0E99 and b['lower']['x']<1.0E99:
            silk_offset=0.12
            module.addRectangle([b['lower']['x']-silk_offset, b['lower']['y']-silk_offset], [b['higher']['x']+silk_offset, b['higher']['y']+silk_offset], 'F.SilkS', 0.12)
            printer.green('added silkscreen rectangle around drawing')
        else:
            printer.red('unable to add silkscreen rectangle around drawing')
    if n_violations == 0 and not args.silent and args.rotate==0:
        printer.green('checking module: {mod}'.format(mod = module.name))
        printer.light_green('No violations found', indentation=2)
        if args.addsilkscreenrect:
            module.save()
    else:
        exit_code += 1
                   
        if args.fix or args.rotate!=0:
            module.save()

if args.fix:
    printer.light_red('Please, resave the files using KiCad to keep indentation standard.')

sys.exit(exit_code)
