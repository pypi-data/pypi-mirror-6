allset
======

A small python utility for auto-completing `__all__` and binding sub-modules in `__init__.py` files.

## How to Use
Add these lines to the top of your `__init__.py`.

    import allset
    allset.set_all_submodules(globals())
    allset.bind_all_submodules(globals())
    del allset

Now you can reference any sub-module with `import mysubmodule` or `from mysubmodule import SubModClassDef`. Additionally, the `from mymodule import *` will work as though you specified all sub-modules in `__all__` manually.

## What's it do?
* `set_all_submodules` sets up you `__all__` variable by auto-detecting the files and sub-modules in the current directory.
* `bind_all_submodules` takes the submodules found in  `set_all_submodules` and applies them to the current namespace.
