# -*- coding: utf-8 -*-

from rules.rule import *
import os

SYSMOD_PREFIX = "${KISYS3DMOD}/"

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Rule 10.4', '3D model reference')

    def checkModel(self, model):
    
        error = False
        
        # Allowed model types
        extensions = ["step","stp","wrl"]
        
        model = model['file']
    
        if model.startswith(SYSMOD_PREFIX):
            model = model.replace(SYSMOD_PREFIX,"")
            
        try:
            model_dir = os.path.dirname(model)
            fn = os.path.basename(model).split(".")
            model_file = ".".join(fn[:-1])
            model_ext = fn[-1]
        except:
            self.addMessage("Model '{mod}' is invalid path".format(mod=model))
            return True
            
        if not model_ext.lower() in extensions:
            self.addMessage("Model '{mod}' is incompatible format (must be STEP or WRL file)".format(mod=model))
            return True
        
        fp_dir = self.module_dir[0] + ".3dshapes"
        fp_name = self.module.name
        
        if not model_dir == fp_dir:
            self.addMessage("3D model directory is different from footprint directory (found '{n1}', should be '{n2}')".format(n1=model_dir, n2=fp_dir))
            error = True
        if not model_file == fp_name:
            self.addMessage("3D model name is different from footprint name (found '{n1}', should be '{n2}')".format(n1=model_file, n2=fp_name))
            error = True
            
        return error
        
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

        models = module.models
        
        if len(models) == 0:
            # Warning msg
            self.addMessage("Warning: No 3D model provided")
            return False
        
        if len(models) > 1:
            self.addMessage("Warning: More than one 3D model provided")
            
        model_error = False
            
        for model in models:
            if self.checkModel(model):
                model_error = True
                
        return model_error

    def fix(self):
        self.addFixMessage("Fix not supported")
