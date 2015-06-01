# -*- coding: utf-8 -*-

from rules.rule import *
import os

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module):
        super(Rule, self).__init__(module, 'Rule 10.7', '3D Shape ".wrl" files are named the same as their footprint and are placed in a folder named the same as the footprint library replacing the ".pretty" with ".3dshapes".')

    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * module_dir
            * model_dir
            * model_file
        """
        module = self.module
        module_dir = os.path.split(os.path.dirname(os.path.realpath(module.filename)))[-1]
        self.module_dir = os.path.splitext(module_dir)

        if len(module.models) == 0:
            return False
        elif len(module.models) > 1:
            return True

        model_file_path = module.models[0]['file']
        self.model_file = os.path.splitext(os.path.basename(model_file_path))
        model_dir = os.path.split(os.path.dirname(model_file_path))[-1]
        self.model_dir = os.path.splitext(model_dir)

        if (self.model_file[0] == module.name and
            self.model_file[1] == '.wrl' and
            self.model_dir[0] == self.module_dir[0] and
            self.model_dir[1] == '.3dshapes'):
            return False

        return True

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.check():
            if len(module.models) == 1:
                path = os.path.join(self.module_dir[0] + '.3dshapes', module.name + '.wrl')
                module.models[0]['file'] = path
            elif len(module.models) > 1:
                pass
                # TODO
