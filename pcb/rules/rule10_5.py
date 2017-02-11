# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        self.expected_ref_thickness=0.15
        self.expected_ref_width=1
        super(Rule, self).__init__(module, 'Rule 10.5', "Reference designator has a height of {0}mm or smaller if needed, thickness of {1}mm and is placed on the silkscreen and the fabrication layer.".format(self.expected_ref_width,self.expected_ref_thickness))

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        ok=False
        
        needs_secondrefdes=True
        secondrefdeslayer='F.Fab'
        secondrefdespos=module.reference['pos']
        secondrefdesfont=module.reference['font']
        secondrefdestext='%R'
        secondrefdes=[]
        if module.reference['layer'] == 'B.SilkS':
            secondrefdeslayer='B.Fab';
        elif module.reference['layer'] == 'F.Fab':
            secondrefdeslayer='F.SilkS';
        elif module.reference['layer'] == 'B.Fab':
            secondrefdeslayer='B.SilkS'
        
        for txt in module.userText:
            if txt['user']=='%R' and txt['layer']==secondrefdeslayer:
                needs_secondrefdes=False
                secondrefdes=txt
                secondrefdespos=txt['pos']
                secondrefdeslayer=txt['layer']
                secondrefdestext=txt['user']
            if txt['user']=='%R' and txt['layer']!=secondrefdeslayer:
                needs_secondrefdes=False
                self.verbose_message=self.verbose_message+"Found user-text reference label (text='%R') on layer '{0}', but expected it on layer '{1}'!\n".format(txt['layer'], secondrefdeslayer)
                secondrefdes=txt
                secondrefdespos=txt['pos']
                secondrefdeslayer=txt['layer']
                secondrefdestext=txt['user']
                ok=False
        secondrefdesfont={'width': self.expected_ref_width, 'height': self.expected_ref_width, 'thickness': self.expected_ref_thickness, 'italic': False}
        module.secondrefdespos=secondrefdespos
        module.secondrefdesfont=secondrefdesfont
        module.secondrefdeslayer=secondrefdeslayer
        module.needs_secondrefdes=needs_secondrefdes
                
        if module.reference['layer'] != 'F.SilkS' and module.reference['layer'] != 'B.SilkS':
            self.verbose_message=self.verbose_message+"Reference label is on layer '{0}', but should be on layer F.SilkS or B.SilkS!\n".format(module.reference['layer'])
            ok=True
        if module.reference['layer'] != 'F.SilkS' and module.reference['layer'] != 'B.SilkS':
            self.verbose_message=self.verbose_message+"Reference label is on layer '{0}', but should be on layer F.SilkS or B.SilkS!\n".format(module.reference['layer'])
            ok=True
        if (module.reference['font']['height'] > self.expected_ref_width):
            self.verbose_message=self.verbose_message+"Reference label has a height of {1}mm (expected: <={0}mm).\n".format(self.expected_ref_width,module.reference['font']['height'])
            ok= True
        if (module.reference['font']['width'] > self.expected_ref_width):
            self.verbose_message=self.verbose_message+"Reference label has a width of {1}mm (expected: <={0}mm).\n".format(self.expected_ref_width,module.reference['font']['width'])
            ok= True
        if (module.reference['font']['thickness'] != self.expected_ref_thickness):
            self.verbose_message=self.verbose_message+"Reference label has a thickness of {1}mm (expected: {0}mm).\n".format(self.expected_ref_thickness,module.reference['font']['thickness'])
            ok= True
        if needs_secondrefdes:
            self.verbose_message=self.verbose_message+"Reference label should also be available on layer '{0}'.\n".format(secondrefdeslayer)
            ok= True
        if len(secondrefdes)>0:
            if (secondrefdes['font']['height'] > self.expected_ref_width):
                self.verbose_message=self.verbose_message+"User-text reference label (text='%R') has a height of {1}mm (expected: <={0}mm).\n".format(self.expected_ref_width,secondrefdes['font']['height'])
                ok= True
            if (secondrefdes['font']['width'] > self.expected_ref_width):
                self.verbose_message=self.verbose_message+"User-text reference label (text='%R') has a width of {1}mm (expected: <={0}mm).\n".format(self.expected_ref_width,secondrefdes['font']['width'])
                ok= True
            if (secondrefdes['font']['thickness'] != self.expected_ref_thickness):
                self.verbose_message=self.verbose_message+"User-text reference label (text='%R') has a thickness of {1}mm (expected: {0}mm).\n".format(self.expected_ref_thickness,secondrefdes['font']['thickness'])
                ok= True
        
        return ok
        

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.reference['value'] = 'REF**'
            module.reference['layer'] = 'F.SilkS'
            module.reference['font']['width'] = self.expected_ref_width
            module.reference['font']['height'] = self.expected_ref_width
            module.reference['font']['thickness'] = self.expected_ref_thickness
            
            if module.needs_secondrefdes:
                txt={'user': '%R', 'pos': module.secondrefdespos, 'layer': module.secondrefdeslayer, 'font': module.secondrefdesfont, 'hide': False } 
                module.userText.append(txt)
                print('added second REFDES')
            else:
                for txt in range(0,len(module.userText)):
                    if module.userText[txt]['user']=='%R':
                        print('OLD: ', module.userText[txt])
                        module.userText[txt]['pos']=module.secondrefdespos
                        module.userText[txt]['layer']=module.secondrefdeslayer
                        module.userText[txt]['font']=module.secondrefdesfont
                        print('NEW: ', module.userText[txt])
                        print('fixed second REFDES ', txt)
                        break
                        
                        