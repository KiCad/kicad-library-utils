# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        self.expected_ref_thickness=0.15
        self.expected_ref_width=1
        super(Rule, self).__init__(module, 'Rule 10.5', "Reference designator has a height of {0}mm or smaller if needed, thickness of {1}mm and is placed on the silkscreen layer.".format(self.expected_ref_width,self.expected_ref_thickness))

    def check(self):
        """
        Proceeds the checking of the rule.
        """
        module = self.module
        ok=False

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
