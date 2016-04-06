import glob
import importlib
import inspect
import os

from ._interpreter import Interpreter


def is_valid_plugin(plugin):
    return os.path.isfile(plugin) and not os.path.basename(plugin).startswith('_')

package_dir = 'loader.plugins'

packages_to_import = [package for package in glob.glob(os.path.dirname(__file__) + '/*.py') if is_valid_plugin(package)]

packages = [importlib.import_module('.' + os.path.basename(package)[:-3], package_dir) for package in packages_to_import]

plugins = []

for package in packages:
    for value in package.__dict__.values():
        if inspect.isclass(value) and issubclass(value, Interpreter) and value is not Interpreter:
            plugins.append(value)