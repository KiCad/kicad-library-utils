# -*- coding: utf-8 -*-

from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'EC03 - Extra Checking', 'Check part reference, name and footprint position and alignment')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * recommended_ref_pos
            * recommended_ref_alignment
            * recommended_name_pos
            * recommended_name_alignment
            * recommended_fp_pos
            * recommended_fp_alignment
            * fp_is_missing
        """

        # check if component has just one rectangle
        if len(self.component.draw['rectangles']) != 1: return False

        top = max(int(self.component.draw['rectangles'][0]['starty']), int(self.component.draw['rectangles'][0]['endy']))
        bottom = min(int(self.component.draw['rectangles'][0]['starty']), int(self.component.draw['rectangles'][0]['endy']))

        ## reference checking

        # if there is no pins in the top, the recommended position to ref is at top-center, horizontally centered
        if len(self.component.filterPins(direction='D')) == 0:
            self.recommended_ref_pos = (0, top + 125)
            self.recommended_ref_alignment = 'C'

        # otherwise, the recommended is put it before the first pin x position, right-aligned
        else:
            x = min([int(i['posx']) for i in self.component.filterPins(direction='D')]) - 100
            self.recommended_ref_pos = (x, top + 125)
            self.recommended_ref_alignment = 'R'

        # get the current reference infos and compare them to recommended ones
        ref_need_fix = False
        pos = (int(self.component.fields[0]['posx']), int(self.component.fields[0]['posy']))
        if (pos != self.recommended_ref_pos or
            self.component.fields[0]['htext_justify'] != self.recommended_ref_alignment):
            ref_need_fix = True

        ## name checking

        # if there is no pins in the top, the recommended position to name is at top-center, horizontally centered
        if len(self.component.filterPins(direction='D')) == 0:
            self.recommended_name_pos = (0, top + 50)
            self.recommended_name_alignment = 'C'

        # otherwise, the recommended is put it before the first pin x position, right-aligned
        else:
            x = min([int(i['posx']) for i in self.component.filterPins(direction='D')]) - 100
            self.recommended_name_pos = (x, top + 50)
            self.recommended_name_alignment = 'R'

        # get the current name infos and compare them to recommended ones
        name_need_fix = False
        pos = (int(self.component.fields[1]['posx']), int(self.component.fields[1]['posy']))
        if (pos != self.recommended_name_pos or
            self.component.fields[1]['htext_justify'] != self.recommended_name_alignment):
            name_need_fix = True

        ## footprint checking

        # if there is no pins in the bottom, the recommended position to footprint is at bottom-center, horizontally centered
        if len(self.component.filterPins(direction='U')) == 0:
            self.recommended_fp_pos = (0, bottom - 50)
            self.recommended_fp_alignment = 'C'

        # otherwise, the recommended is put it after the last pin x position, left-aligned
        else:
            x = max([int(i['posx']) for i in self.component.filterPins(direction='U')]) + 50
            self.recommended_fp_pos = (x, bottom - 50)
            self.recommended_fp_alignment = 'L'

        # get the current footprint infos and compare them to recommended ones
        fp_need_fix = False
        self.fp_is_missing = False
        if len(self.component.fields) >= 3:
            pos = (int(self.component.fields[2]['posx']), int(self.component.fields[2]['posy']))
            if (pos != self.recommended_fp_pos or
                self.component.fields[2]['htext_justify'] != self.recommended_fp_alignment):
                fp_need_fix = True
        else:
            fp_need_fix = True
            self.fp_is_missing = True

        return True if (ref_need_fix or name_need_fix or fp_need_fix) else False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        if self.check():
            self.component.fields[0]['posx'] = str(self.recommended_ref_pos[0])
            self.component.fields[0]['posy'] = str(self.recommended_ref_pos[1])
            self.component.fields[0]['htext_justify'] = self.recommended_ref_alignment

            self.component.fields[1]['posx'] = str(self.recommended_name_pos[0])
            self.component.fields[1]['posy'] = str(self.recommended_name_pos[1])
            self.component.fields[1]['htext_justify'] = self.recommended_name_alignment

            if not self.fp_is_missing:
                self.component.fields[2]['posx'] = str(self.recommended_fp_pos[0])
                self.component.fields[2]['posy'] = str(self.recommended_fp_pos[1])
                self.component.fields[2]['htext_justify'] = self.recommended_fp_alignment
