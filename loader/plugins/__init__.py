import glob
import importlib
import inspect
import os

from ._interpreter import Interpreter


def is_valid_plugin(plugin):
    """
    Ensure a plugin is valid - i.e. it is a file and doesn't start with _ (e.g. __init__).

    :param plugin: str, filepath to a package.
    :return: bool, is it valid?
    """
    return os.path.isfile(plugin) and not os.path.basename(plugin).startswith('_')

_PACKAGE_DIR = 'loader.plugins'  # We are always going to be seeing this file from 2 directories up.

# Get the valid packages
_PACKAGES_TO_IMPORT = [package for package in glob.glob(os.path.dirname(__file__) + '/*.py') if is_valid_plugin(package)]

# import them all.
_PACKAGES = [importlib.import_module('.' + os.path.basename(package)[:-3], _PACKAGE_DIR) for package in _PACKAGES_TO_IMPORT]

PLUGINS = []

for package in _PACKAGES:
    for value in package.__dict__.values():  # loop through all the packages items and grab intepreters.
        if inspect.isclass(value) and issubclass(value, Interpreter) and value is not Interpreter:
            PLUGINS.append(value)