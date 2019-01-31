# -*- coding: utf-8 -*-

from rules.rule import *


class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, component):
        super(Rule, self).__init__(component, 'Pin name position offset')

    def check(self):

        offset = int(self.component.definition['text_offset'])

        if self.component.definition['draw_pinname'] == 'N':
            # If the pin names aren't drawn, the offset doesn't matter.
            return False
        elif offset == 0:
            # An offset of 0 means the text is placed outside the symbol,
            # rather than inside.  As the rules about offset only apply when
            # the text is inside the symbol, this case is perfectly OK.
            return False
        elif offset > 50:
            self.error("Pin offset outside allowed range")
            self.errorExtra("Pin offset ({o}) must not be above 50mils".format(o=offset))
            return True
        elif offset < 20:
            self.warning("Pin offset outside allowed range")
            self.warningExtra("Pin offset ({o}) should not be below 20mils".format(o=offset))
            return True
        elif offset > 20:
            self.warning("Pin offset not preferred value")
            self.warningExtra("Pin offset ({o}) should be 20mils unless"
                    " required by symbol geometry".format(o=offset))

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        self.info("Fixing, assuming typical symbol geometry...")
        self.component.definition['text_offset'] = '20'

        self.recheck()
