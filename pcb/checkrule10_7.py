# -*- coding: utf-8 -*-

import os

def get_names(module):
    module_dir = module_dir = os.path.split(os.path.dirname(module.filename))[-1]
    module_dir = os.path.splitext(module_dir)

    model_file_path = module.models[0]['file']
    model_file = os.path.splitext(os.path.basename(model_file_path))
    model_dir = os.path.split(os.path.dirname(model_file_path))[-1]
    model_dir = os.path.splitext(model_dir)

    return (module_dir, model_dir, model_file)

# returns true if a violation is found
def check_rule(module):
    if not module.models: return False
    if len(module.models) > 1: return True

    module_dir, model_dir, model_file = get_names(module)

    if (model_file[0] == module.name and
        model_file[1] == '.wrl' and
        model_dir[0] == module_dir[0] and
        model_dir[1] == '.3dshapes'):
        return False

    return True

def fix_rule(module):
    # first check if it's violating the rule
    if not check_rule(module): return

    # TODO: warning if more than 1 model

    if len(module.models) == 1:
        module_dir, model_dir, model_file = get_names(module)
        path = os.path.join(module_dir[0] + '.3dshapes', module.name + '.wrl')
        module.models[0]['file'] = path
