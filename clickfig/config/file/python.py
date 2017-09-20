from __future__ import absolute_import

import imp
import inspect
import os
import re

from .base import BaseConfigFile, ConfigReadResult, flatten_dict
from ...base import return_key_value


# TODO: Python 3 compatibility
def import_module(module_file):
    """
    Given a path to a Python file, this function imports it and returns the imported module.

    :param str module_file: The filename of the module that you wish to include.
    """

    module_name = re.sub("\.py$", "", os.path.split(module_file)[-1])
    module_dir = os.path.abspath(os.path.dirname(module_file))

    f, filename, description = imp.find_module(module_name, [module_dir])
    return imp.load_module(module_name, f, filename, description)


class PythonConfigFile(BaseConfigFile):
    def read(self, key=None, flatten=True):
        if not self.exists():
            return None

        config_module = import_module(self.name)

        data = {
            k: v for k, v in inspect.getmembers(config_module) if
            k not in ["__builtins__", "__doc__", "__name__", "__package__", "__file__"]
        }

        result = return_key_value(data, key=key)

        if flatten and isinstance(result, dict):
            result = flatten_dict(result, separator=self.separator)

        result = ConfigReadResult(result, key=key, separator=self.separator)

        return result

    def write(self, key, value, read_existing_data=True):

        raise NotImplementedError
