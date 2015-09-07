# -*- coding: utf-8 -*-
from rules.rule import *
import cmath
class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 6.5', 'Silkscreen is not superposed to pads, its outline is completely visible after board assembly, uses 0.15mm line width and provides a reference mark for pin 1. (IPC-7351).')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_silk
            * b_silk
            * bad_width
        """
        module = self.module
        self.f_silk = module.filterGraphs('F.SilkS')
        self.b_silk = module.filterGraphs('B.SilkS')

        # check the width
        self.bad_width = []
        
        
        for graph in (self.f_silk + self.b_silk):
            if graph['width'] != 0.15:
                self.bad_width.append(graph)
        # check intersections between line and pad, translate the line and pad to coordinate (0,0), rotate the line and pad 
        self.intersections=[]
        
        for graph in (self.f_silk + self.b_silk):
            if 'angle' in graph:
                #TODO
                pass
            elif 'center' in graph:
                #TODO
                pass
            else:
                for pad in module.pads:
                    padComplex=complex(pad['pos']['x'],pad['pos']['y'])
                    startComplex=complex(graph['start']['x'],graph['start']['y'])
                    endComplex=complex(graph['end']['x'],graph['end']['y'])
                    if endComplex.imag>startComplex.imag:
                        vector=endComplex-startComplex
                        padComplex=padComplex-startComplex
                    else:
                        vector=startComplex-endComplex
                        padComplex=padComplex-endComplex
                    length=abs(vector)
                    vectorR=cmath.rect(1,-cmath.phase(vector))
                    padComplex=padComplex*vectorR
                    if (padComplex.real-pad['size']['x']/2)<length and (padComplex.real+pad['size']['x']/2)>0:
                        if abs(padComplex.imag)<pad['size']['x']/2+0.075:
                            self.intersections.append([pad,graph])
        return True if (len(self.bad_width) or len(self.intersections)) else False
    

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            for graph in self.bad_width:
                graph['width'] = 0.15
