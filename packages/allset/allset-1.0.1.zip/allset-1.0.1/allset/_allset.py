import os, pkgutil, sys, glob

def _get_module_directory(namespace):
    return os.path.dirname(namespace['__file__'])

def _get_module_name(namespace):
    return namespace['__name__']
    #return os.path.basename(_get_module_directory(namespace))

def _get_submodules(namespace):
    return list(pkgutil.iter_modules([_get_module_directory(namespace)]))

def _assign_modules_names(filter_mods, namespace, import_modules):
    namespace['__all__'] = filter_mods([module[1] for module in import_modules])
    return namespace['__all__']

def _pass_through(arg):
    return arg

def _load_modules(namespace, import_modules):
    for module_loader, name, ispkg in import_modules:
        submodule = '.'.join([_get_module_name(namespace), name])
        if submodule in sys.modules:
            module = sys.modules[submodule]
        else:
            module = module_loader.find_module(submodule).load_module(submodule)
        namespace[name] = module

def set_all_submodules(namespace, filter_mods=None):
    return _assign_modules_names(filter_mods or _pass_through, namespace, _get_submodules(namespace))

def bind_all_submodules(namespace):
    _load_modules(namespace, _get_submodules(namespace))
