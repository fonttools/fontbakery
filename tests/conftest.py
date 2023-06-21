import importlib
import sys


def reload_module(module_name):
    module = importlib.import_module(module_name)
    importlib.reload(module)


class ImportRaiser:
    def __init__(self, module_name: str):
        self.module_name = module_name

    def find_spec(self, fullname, path, target=None):
        if fullname == self.module_name:
            raise ImportError()


def remove_import_raiser(module_name):
    for item in sys.meta_path:
        if hasattr(item, "module_name") and item.module_name == module_name:
            sys.meta_path.remove(item)
