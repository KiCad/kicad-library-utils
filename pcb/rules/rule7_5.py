# -*- coding: utf-8 -*-

from __future__ import division

# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

from rules.rule import *
import re, os, math

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        self.expected_width=0.05
        self.expected_grid=0.01
        super(Rule, self).__init__(module, args, 'Rule 6.6', "Courtyard line has a width {0}mm. This line is placed so that its clearance is measured from its center to the edges of pads and body, and its position is rounded on a grid of {1}mm.".format(self.expected_width,self.expected_grid))
        
    def _getComponentAndPadBounds(self):
        module = self.module
        overpadBounds=module.overpadsBounds()
        geoBounds=module.geometricBounds('F.Fab')
        #print('overpadBounds=',overpadBounds)
        #print('F.Fab: geoBounds=',geoBounds)
        b={'lower':{'x':1.0E99, 'y':1.0E99},'higher':{'x':-1.0E99, 'y':-1.0E99}}
        if (geoBounds['lower']['x']>1.0E98 and geoBounds['lower']['x']==geoBounds['lower']['y']) or (geoBounds['higher']['x']<-1.0e98 and geoBounds['higher']['x']==geoBounds['higher']['y']):
            geoBounds=module.geometricBounds('B.Fab')               
            #print('B.Fab: geoBounds=',geoBounds)
        if (geoBounds['lower']['x']>1.0E98 and geoBounds['lower']['x']==geoBounds['lower']['y']) or (geoBounds['higher']['x']<-1.0e98 and geoBounds['higher']['x']==geoBounds['higher']['y']):
            geoBounds=module.geometricBounds('F.SilkS')
            #print('F.SilkS: geoBounds=',geoBounds)
        if (geoBounds['lower']['x']>1.0E98 and geoBounds['lower']['x']==geoBounds['lower']['y']) or (geoBounds['higher']['x']<-1.0e98 and geoBounds['higher']['x']==geoBounds['higher']['y']):
            geoBounds=module.geometricBounds('B.SilkS')
            #print('B.SilkS: geoBounds=',geoBounds)
        
        b['lower']['x']=min(b['lower']['x'],overpadBounds['lower']['x'])
        b['lower']['y']=min(b['lower']['y'],overpadBounds['lower']['y'])
        b['higher']['x']=max(b['higher']['x'],overpadBounds['higher']['x'])
        b['higher']['y']=max(b['higher']['y'],overpadBounds['higher']['y'])
        b['lower']['x']=min(b['lower']['x'],geoBounds['lower']['x'])
        b['lower']['y']=min(b['lower']['y'],geoBounds['lower']['y'])
        b['higher']['x']=max(b['higher']['x'],geoBounds['higher']['x'])
        b['higher']['y']=max(b['higher']['y'],geoBounds['higher']['y'])
        
        return b
        
    def _getCrtRectangle(self):
        # searches for a series of consecutive lines (last.end==next.start or last.start==next.end)
        # by picking a start point and following it until we return
        lines=self.f_courtyard_lines
        self.courtyard_rectangle_layer='F'
        if len(lines)==0:
            lines=self.b_courtyard_lines
            if len(lines)>0:
                self.courtyard_rectangle_layer='B'
        if len(lines)<4:
            # rectangle needs to have at least 4 lines
            return { 'x': 0, 'y':0, 'width':0, 'height':0}
        else:
            x0={'x': min(lines[0]['start']['x'],lines[0]['end']['x']), 'y': min(lines[0]['start']['y'],lines[0]['end']['y'])}
            start=lines[0]['start']
            next=lines[0]['end']
            currentPos=start
            width=math.fabs(lines[0]['end']['x']-lines[0]['start']['x'])
            height=math.fabs(lines[0]['end']['y']-lines[0]['start']['y'])
            corners_found=1
            used_lines=[]
            #print(-1, 0,': start=',start,'   next=',next)
            for corners in range(0,4):
                # find 4 corners of rectangle
                found=False
                for li in range(1,len(lines)):
                    if not li in used_lines:
                        if lines[li]['end']['x']-lines[li]['start']['x']==0 or lines[li]['end']['y']-lines[li]['start']['y']==0:
                            # we only look at rectangles formed from hor./ver. lines
                            if lines[li]['start']==next:
                                next=lines[li]['end']
                                currentPos=lines[li]['start']
                                found=True
                            elif lines[li]['end']==next:
                                next=lines[li]['start']
                                currentPos=lines[li]['end']
                                found=True
                            if found:
                                used_lines.append(li)
                                width=max(width,math.fabs(lines[li]['end']['x']-lines[li]['start']['x']))
                                height=max(height,math.fabs(lines[li]['end']['y']-lines[li]['start']['y']))
                                x0={
                                    'x': min(x0['x'], lines[li]['start']['x'],lines[li]['end']['x']), 
                                    'y': min(x0['y'], lines[li]['start']['y'],lines[li]['end']['y'])}
                    if found:
                        corners_found=corners_found+1
                        break
                    if next==start:
                        break
                #print(corners_found, found,': next=',next,'   currentPos=',currentPos)
            #print("corners_found=",corners_found, "   currentPos=",currentPos,"  start=",start,"  next=",next)
            
            if corners_found==4 and next==start:
                #print("x0=", x0, "  width=",width,"  height=",height)
                return { 'x': x0['x'], 'y':x0['y'], 'width':width, 'height':height}
            else:
                #print("NOT FOUND!!!")
                return { 'x': 0, 'y':0, 'width':0, 'height':0}
        

    def _calcCourtyardOffset(self):
        module = self.module
        module_dir = os.path.split(os.path.dirname(os.path.realpath(module.filename)))[-1]
        self.module_dir = "{0}".format(os.path.splitext(module_dir))
        crt_offset=0.25
        b=self._getComponentAndPadBounds()
        if (b['higher']['x']-b['lower']['x']<2 and b['higher']['y']-b['lower']['y']<0.9) or (b['higher']['x']-b['lower']['x']<0.9 and b['higher']['y']-b['lower']['y']<2):
            crt_offset=0.15
        if re.match("BGA\-.*", module.name) or re.match(".*Housing.*BGA.*", module_dir):
            crt_offset=1
        elif re.match(".*Connector.*", module.name) or re.match(".*Connector.*", self.module_dir) or re.match(".*Socket.*", module.name) or re.match(".*Socket.*", self.module_dir) or re.match(".*Button.*", module.name) or re.match(".*Button.*", self.module_dir) or re.match(".*Switch.*", module.name) or re.match(".*Switch.*", self.module_dir) :
            crt_offset=0.5
        return crt_offset

    def _calcCourtyardRectangle(self):
        b=self._getComponentAndPadBounds()
        if b['higher']['x']!=b['lower']['x'] and b['higher']['y']!=b['lower']['y'] and b['higher']['x']>-1.0E99 and b['higher']['y']>-1.0E99 and b['lower']['x']<1.0E99 and b['lower']['x']<1.0E99:
            crt_offset=self._calcCourtyardOffset()
            factor=1/self.expected_grid
            return { 'x': math.floor((b['lower']['x']-crt_offset)*factor)/factor, 
                    'y':math.floor((b['lower']['y']-crt_offset)*factor)/factor, 
                    'width':math.ceil((math.fabs(b['higher']['x']-b['lower']['x'])+2*crt_offset)*factor)/factor, 
                    'height':math.ceil((math.fabs(b['higher']['y']-b['lower']['y'])+2*crt_offset)*factor)/factor
                   }
        else:
            return { 'x': 0, 'y':0, 'width':0, 'height':0}

        
    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_courtyard_all
            * b_courtyard_all
            * f_courtyard_lines
            * b_courtyard_lines
            * bad_width
            * bad_grid
            * crt_offset
            * actual_crt_rectangle
            * expected_crt_rectangle
            * courtyard_rectangle_layer
        """
        
        error = False

        module = self.module
        self.f_courtyard_all = module.filterGraphs('F.CrtYd')
        self.b_courtyard_all = module.filterGraphs('B.CrtYd')

        # check the width
        self.bad_width = []
        for graph in (self.f_courtyard_all + self.b_courtyard_all):
            if graph['width'] != self.expected_width:
                self.bad_width.append(graph)

        self.f_courtyard_lines = module.filterLines('F.CrtYd')
        self.b_courtyard_lines = module.filterLines('B.CrtYd')

        self.crt_offset=self._calcCourtyardOffset()
        self.actual_crt_rectangle=self._getCrtRectangle()
        self.expected_crt_rectangle=self._calcCourtyardRectangle()
        
        if self.actual_crt_rectangle['width']*self.actual_crt_rectangle['width']>0 and self.expected_crt_rectangle['width']*self.expected_crt_rectangle['width']>0:
            crterrorbound=5e-2
            if math.fabs(self.actual_crt_rectangle['x']-self.expected_crt_rectangle['x'])>crterrorbound or math.fabs(self.actual_crt_rectangle['y']-self.expected_crt_rectangle['y'])>crterrorbound or math.fabs(self.actual_crt_rectangle['width']-self.expected_crt_rectangle['width'])>crterrorbound or math.fabs(self.actual_crt_rectangle['height']-self.expected_crt_rectangle['height'])>crterrorbound:
                clearancemin=self.crt_offset-\
                             min(self.expected_crt_rectangle['x']-self.actual_crt_rectangle['x'],\
                                 self.expected_crt_rectangle['y']-self.actual_crt_rectangle['y'],\
                                 self.expected_crt_rectangle['width']+self.expected_crt_rectangle['x']-self.actual_crt_rectangle['width']-self.actual_crt_rectangle['x'],\
                                 self.expected_crt_rectangle['height']+self.expected_crt_rectangle['y']-self.actual_crt_rectangle['height']-self.actual_crt_rectangle['y'])
                clearancemax=self.crt_offset-\
                             max(self.expected_crt_rectangle['x']-self.actual_crt_rectangle['x'],\
                                 self.expected_crt_rectangle['y']-self.actual_crt_rectangle['y'],\
                                 self.expected_crt_rectangle['width']+self.expected_crt_rectangle['x']-self.actual_crt_rectangle['width']-self.actual_crt_rectangle['x'],\
                                 self.expected_crt_rectangle['height']+self.expected_crt_rectangle['y']-self.actual_crt_rectangle['height']-self.actual_crt_rectangle['y'])
                #self.verbose_message=self.verbose_message+"For this footprint a rectangular courtyard {0} was expected, but a courtyard rectangle {1} was found\n".format(self.expected_crt_rectangle,self.actual_crt_rectangle)
                self.addMessage("A courtyard clearance in the range {1}...{2}mm was found, but {0}mm was expected.\nThe recommendet courtyard rectangle would be:\n    {3}mm.".format(self.crt_offset, round(min(clearancemin, clearancemax)*100)/100, round(max(clearancemin, clearancemax)*100)/100, self.expected_crt_rectangle))
                error = True
                
        # check if there is proper rounding 0.01 of courtyard lines
        # convert position to nanometers (add/subtract 1/10^7 to avoid wrong rounding and cast to int)
        # int pos_x = (d_pos_x + ((d_pos_x >= 0) ? 0.0000001 : -0.0000001)) * 1000000;
        # int pos_y = (d_pos_y + ((d_pos_y >= 0) ? 0.0000001 : -0.0000001)) * 1000000;
        self.bad_grid = []
        for line in (self.f_courtyard_lines + self.b_courtyard_lines):
            nanometers = {}
            x, y = line['start']['x'], line['start']['y']
            x = int( (x + (0.0000001 if x >= 0 else -0.0000001))*1E6 )
            y = int( (y + (0.0000001 if y >= 0 else -0.0000001))*1E6 )
            start_is_wrong = (x % int(self.expected_grid*1E6)) or (y % int(self.expected_grid*1E6))
            nanometers['start'] = {'x':x, 'y':y}

            x, y = line['end']['x'], line['end']['y']
            x = int( (x + (0.0000001 if x >= 0 else -0.0000001))*1E6 )
            y = int( (y + (0.0000001 if y >= 0 else -0.0000001))*1E6 )
            end_is_wrong = (x % int(self.expected_grid*1E6)) or (y % int(self.expected_grid*1E6))
            nanometers['end'] = {'x':x, 'y':y}

            if start_is_wrong or end_is_wrong:
                self.bad_grid.append({'nanometers':nanometers, 'line':line})

                
        for  g in self.bad_width:
            self.addMessage("Some courtyard line has a width of {1}mm, different from {0}mm.\n".format(self.expected_width,g['width']))
            error = True
        for  g in self.bad_grid:
            self.addMessage("Some courtyard line is not on the expected grid of {0}mm (line: {1}).\n".format(self.expected_grid,g['line']))
            error = True
        if len(self.f_courtyard_all)+len(self.b_courtyard_all) == 0:
            self.addMessage("No courtyard line was found at all.\n")
            error = True
        
        return error

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            for graph in self.bad_width:
                graph['width'] = self.expected_width

            for item in self.bad_grid:
                x, y = item['nanometers']['start']['x'], item['nanometers']['start']['y']
                x, y = round(x / self.expected_grid*1E6) * self.expected_grid, round(y / self.expected_grid*1E6) * self.expected_grid
                item['nanometers']['start']['x'], item['nanometers']['start']['y'] = x, y

                x, y = item['nanometers']['end']['x'], item['nanometers']['end']['y']
                x, y = round(x / self.expected_grid*1E6) * self.expected_grid, round(y / self.expected_grid*1E6) * self.expected_grid
                item['nanometers']['end']['x'], item['nanometers']['end']['y'] = x, y

            # create courtyard if does not exists
            if len(self.f_courtyard_all)+len(self.b_courtyard_all) == 0:
                if self.expected_crt_rectangle['width']>0 and self.expected_crt_rectangle['height']>0:
                    self.addFixMessage("ADDING Courtyard-RECTANGLE with clearance {0}mm on layer {1}.CrtYd".format(self.crt_offset, self.courtyard_rectangle_layer))
                    module.addRectangle([self.expected_crt_rectangle['x'], self.expected_crt_rectangle['y']], [self.expected_crt_rectangle['x']+self.expected_crt_rectangle['width'], self.expected_crt_rectangle['y']+self.expected_crt_rectangle['height']], self.courtyard_rectangle_layer+'.CrtYd', 0.05)
            
            # modify courtyard rectangle that was wrong (e.g. wrong offset)
            if self.actual_crt_rectangle['width']*self.actual_crt_rectangle['width']>0 and self.expected_crt_rectangle['width']*self.expected_crt_rectangle['width']>0:
                if self.actual_crt_rectangle != self.expected_crt_rectangle:
                    if self.args.fixmore:
                        self.addFixMessage("REPLACING Courtyard with RECTANGLE with clearance {0}mm on layer {1}.CrtYd".format(self.crt_offset, self.courtyard_rectangle_layer))
                        for li in reversed(range(0,len(module.lines))):
                            if module.lines[li]['layer']=='F.CrtYd' or module.lines[li]['layer']=='B.CrtYd':
                                del module.lines[li]
                        module.addRectangle([self.expected_crt_rectangle['x'], self.expected_crt_rectangle['y']], [self.expected_crt_rectangle['x']+self.expected_crt_rectangle['width'], self.expected_crt_rectangle['y']+self.expected_crt_rectangle['height']], self.courtyard_rectangle_layer+'.CrtYd', 0.05)
                    else:
                        self.addFixMessage("Courtyard rectangle was not fixed, use --fixmore to get this fixed!")
                    