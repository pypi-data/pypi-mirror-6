import os, pkgutil, sys

def _get_module_directory(namespace):
    return os.path.dirname(namespace['__file__'])

def _get_module_name(namespace):
    return namespace['__name__']
    #return os.path.basename(_get_module_directory(namespace))

def _get_submodules(namespace):
    return pkgutil.iter_modules([_get_module_name(namespace)])

def set_all_submodules(namespace, filter_mods=None):
    if filter_mods is None:
        filter_mods = lambda m: m

    namespace['__all__'] = filter_mods([module[1] for module in _get_submodules(namespace)])
    return namespace['__all__']
            
def bind_all_submodules(namespace):
    for module_loader, name, ispkg in _get_submodules(namespace):
        submodule = '.'.join([_get_module_name(namespace), name])
        if submodule in sys.modules:
            module = sys.modules[submodule]
        else:
            module = module_loader.find_module(submodule).load_module(submodule)
        namespace[name] = module
