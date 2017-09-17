# -*- coding: utf-8 -*-

from rules.rule import *
import platform

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad lib files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Library files must use Unix-style line endings (LF)')

    def check(self):

        # Only perform this check on linux systems (i.e. Travis)
        # Windows automatically checks out with CR+LF line endings
        if 'linux' in platform.platform().lower() and not self.module.unix_line_endings:
            self.warning("Incorrect line ending")
            self.warningExtra("Library files must use Unix-style line endings (LF)")
            return True

        return False

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """

        f_in = open(self.module.filename('r'))
        data_in = f_in.readall()
        f_in.close()

        if len(data_in) > 0:
            data_out = data_in.replace("\r\n", "\n")
            f_out = open(self.module.filename,'w')
            f_out.write(data_out)
            f_out.close()


        # Re-check line endings
        self.check()
