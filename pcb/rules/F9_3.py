# -*- coding: utf-8 -*-

from rules.rule import *
import os

SYSMOD_PREFIX = "${KISYS3DMOD}/"

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, '3D model reference')

    def checkModel(self, model):

        error = False

        # Allowed model types
        extensions = ["step", "stp", "wrl"]

        model = model['file']
        
        self.model3D_missingSYSMOD = False
        self.model3D_wrongLib = False
        self.model3D_wrongName = False
        self.model3D_wrongFiletype = False
        self.model3D_invalidName = False

        if model.startswith(SYSMOD_PREFIX):
            model = model.replace(SYSMOD_PREFIX,"")
        else:
            self.model3D_missingSYSMOD = True
            self.needsFixMore = True
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
            self.model3D_wrongFiletype = True
            self.needsFixMore = True
            return True

        fp_dir = self.module_dir[0] + ".3dshapes"
        fp_name = self.module.name

        if not model_dir == fp_dir:
            self.error("3D model directory is different from footprint directory (found '{n1}', should be '{n2}')".format(n1=model_dir, n2=fp_dir))
            self.model3D_wrongLib = True
            self.needsFixMore = True
            error = True

        if not model_file == fp_name:
            # Exception for footprints that have additions e.g. "_ThermalPad"
            if fp_name.startswith(model_file) or model_file in fp_name or fp_name in model_file:
                self.warning("3D model name is different from footprint name (found '{n1}', expected '{n2}'), but this might be intentionally!".format(n1=model_file, n2=fp_name))
                self.needsFixMore = True
                self.model3D_wrongName = True
                error = False
                pass
            else:
                self.warning("3D model name is different from footprint name (found '{n1}', expected '{n2}')".format(n1=model_file, n2=fp_name))
                self.needsFixMore = True
                self.model3D_wrongName = True
                error = True

        if not isValidName(model_file):
            error = True
            self.model3D_invalidName = True
            self.error("3D model path '{p}' contains invalid characters as per KLC G1.1".format(
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
        self.no3DModel = False
        fp_dir = self.module_dir[0] + ".3dshapes"
        fp_name = self.module.name
        self.model3D_expectedDir = SYSMOD_PREFIX+fp_dir+'/';
        self.model3D_expectedName = fp_name+'.wrl';
        self.model3D_expectedFullPath = self.model3D_expectedDir+self.model3D_expectedName;
        
        

        if len(models) == 0:
            # Warning msg
            if module.attribute=='virtual':
                # virtual components don't need a 3D model
                self.warning("No 3D model provided for virtual component")
                self.no3DModel = True
                return False
            else:
                self.error("No 3D model provided")
                self.no3DModel = True
                return True

        self.tooMany3DModel = False
        if len(models) > 1:
            self.tooMany3DModel = True
            self.warning("More than one 3D model provided")

        model_error = False

        for model in models:
            if self.checkModel(model):
                model_error = True

        return model_error

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        
        # ensure all variables are set correctly
        if self.no3DModel:
            # model (default)
            model_dict = {'file': self.model3D_expectedFullPath}
            model_dict['pos'] = {'x':0, 'y':0, 'z':0}
            model_dict['scale'] = {'x':1, 'y':1, 'z':1}
            model_dict['rotate'] = {'x':0, 'y':0, 'z':0}
            module.models.append(model_dict)
            self.info("added default model '{model}' to footprint.".format(model=self.model3D_expectedFullPath))
            return
        elif not self.tooMany3DModel and (self.model3D_missingSYSMOD or self.model3D_wrongLib or self.model3D_wrongName):
            if self.args.fixmore:
                # model (default)
                oldpath=module.models[0]['file']
                module.models[0]['file']=self.model3D_expectedFullPath
                self.info("fixed model path from '{oldmodel}' to '{model}'.".format(oldmodel=oldpath, model=self.model3D_expectedFullPath))
                return
            else:
                self.info("Fix not supported by --fix, use --fixmore to fix this!")
                return
                
        self.info("Fix not supported")
        return

    def fixmore(self):
        """
        Proceeds the additional fixing of the rule, if possible and if --fixmore is provided as command-line argument.
        """
        module = self.module
        
        # ensure all variables are set correctly
        if not self.tooMany3DModel and (self.model3D_missingSYSMOD or self.model3D_wrongLib or self.model3D_wrongName):
            # model (default)
            oldpath=module.models[0]['file']
            module.models[0]['file']=self.model3D_expectedFullPath
            self.info("fixed model path from '{oldmodel}' to '{model}'.".format(oldmodel=oldpath, model=self.model3D_expectedFullPath))
            return
                
        self.info("FixMore not supported")
        return
