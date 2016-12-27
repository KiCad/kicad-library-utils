# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        self.expected_val_width=1
        self.expected_val_thickness=0.15
        super(Rule, self).__init__(module, 'Rule 10.4', "Value has a height of {0}mm, thickness of {1}mm, is filled with footprint name and is placed on the fabrication layer.".format(self.expected_val_width,self.expected_val_thickness))

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        ok=False
        if module.value['value'] != module.name:
            self.verbose_message=self.verbose_message+"Contents of value label ('{0}') is different from module name '{1}'!\n".format(module.value['value'], module.name)
            ok=True
        if module.value['layer'] not in ['F.Fab', 'B.Fab']:
            self.verbose_message=self.verbose_message+"Value label is on layer '{0}', but should be on layer F.Fab or B.Fab!\n".format(module.value['layer'])
            ok=True
        if (module.value['font']['height'] != self.expected_val_width):
            self.verbose_message=self.verbose_message+"Value label has a height of {1}mm (expected: {0}mm).\n".format(self.expected_val_width,module.value['font']['height'])
            ok= True
        if (module.value['font']['width'] != self.expected_val_width):
            self.verbose_message=self.verbose_message+"Value label has a width of {1}mm (expected: {0}mm).\n".format(self.expected_val_width,module.value['font']['width'])
            ok= True
        if (module.value['font']['thickness'] != self.expected_val_thickness):
            self.verbose_message=self.verbose_message+"Value label has a thickness of {1}mm (expected: {0}mm).\n".format(self.expected_val_thickness,module.value['font']['thickness'])
            ok= True
            
        return ok
        

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            module.value['value'] = module.name
            module.value['layer'] = 'F.Fab'
            module.value['font']['height'] = self.expected_val_width
            module.value['font']['width'] = self.expected_val_width
            module.value['font']['thickness'] = self.expected_val_thickness