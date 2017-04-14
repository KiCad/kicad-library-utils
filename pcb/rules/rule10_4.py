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
        else:
            self.warning("Model path should start with '" + SYSMOD_PREFIX + "'")
            
        model_split = model.split("/")
        if len(model_split) <= 1:
            model_split = model.split("\\")
        
        if len(model_split) <= 1:
            model_dir = ""
            filename = model_split[0]
        else:
            model_dir = os.path.join(*model_split[:-1])
            filename = model_split[-1]
            
        fn = filename.split(".")
        model_file = ".".join(fn[:-1])
        model_ext = fn[-1]
            
        if not model_ext.lower() in extensions:
            self.error("Model '{mod}' is incompatible format (must be STEP or WRL file)".format(mod=model))
            return True
        
        fp_dir = self.module_dir[0] + ".3dshapes"
        fp_name = self.module.name
        
        if not model_dir == fp_dir:
            self.error("3D model directory is different from footprint directory (found '{n1}', should be '{n2}')".format(n1=model_dir, n2=fp_dir))
            error = True
            
        if not model_file == fp_name:
            # Exception for footprints that have additions e.g. "_ThermalPad"
            if fp_name.startswith(model_file) or model_file in fp_name or fp_name in model_file:
                self.warning("3D model name is different from footprint name (found '{n1}', expected '{n2}')".format(n1=model_file, n2=fp_name))
            else:
                self.error("3D model name is different from footprint name (found '{n1}', should be '{n2}')".format(n1=model_file, n2=fp_name))
                error = True
            
        if not isValidName(model_file):
            error = True
            self.error("3D model path '{p}' contains invalid characters as per KLC 1.7".format(
                p = model_file))
            
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
            self.warning("No 3D model provided")
            return False
        
        if len(models) > 1:
            self.warning("More than one 3D model provided")
            
        model_error = False
            
        for model in models:
            if self.checkModel(model):
                model_error = True
                
        return model_error

    def fix(self):
        self.info("Fix not supported")
