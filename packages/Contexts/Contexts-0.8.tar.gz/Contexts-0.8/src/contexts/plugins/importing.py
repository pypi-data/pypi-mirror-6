import argparse
import importlib
import os
import sys
from .shuffling import Shuffler


class Importer(object):
    @classmethod
    def locate(cls):
        # this is such a hack :(
        # Just trying to get the tests for __main__ to pass.
        # hopefully I can delete those tests (and this method) soon since the
        # logic of __main__ will be much simpler
        return (Shuffler, None)
    def setup_parser(self, parser):
        try:
            parser.add_argument('--no-assert',
                action='store_false',
                dest='rewriting',
                default=True,
                help='Disable assertion rewriting.')
        except argparse.ArgumentError:  # just means it's already been set up
            pass
    def initialise(self, args, env):
        return not args.rewriting

    def import_module(self, dir_path, module_name):
        filename = resolve_filename(dir_path, module_name)
        prune_sys_dot_modules(module_name, filename)
        if module_name in sys.modules:
            return

        loader = self.get_loader(module_name, filename)
        return loader.load_module(module_name)

    def get_loader(self, module_name, filename):
        return importlib.machinery.SourceFileLoader(module_name, filename)

    def __eq__(self, other):
        return (type(self) == type(other))


def resolve_filename(dir_path, module_name):
    filename = os.path.join(dir_path, *module_name.split('.'))
    if os.path.isdir(filename):  # it's a package
        filename = os.path.join(filename, '__init__.py')
    else:
        filename += '.py'
    return filename


def prune_sys_dot_modules(module_name, module_location):
    if module_name in sys.modules:
        existing_module = sys.modules[module_name]
        if not same_file(existing_module.__file__, module_location):
            del sys.modules[module_name]


def same_file(path1, path2):
    return os.path.realpath(path1) == os.path.realpath(path2)
