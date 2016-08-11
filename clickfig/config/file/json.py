import json
import os
from collections import OrderedDict

import dpath

from .base import BaseConfigFile, ConfigReadResult, flatten_dict

from ...base import return_key_value


class JSONConfigFile(BaseConfigFile):
    def read(self, key=None, flatten=True):

        if not self.exists():
            return None

        with open(self.name) as f:
            data = json.loads(f.read(), object_pairs_hook=OrderedDict)

        result = return_key_value(data, key=key)

        if flatten and isinstance(result, dict):
            result = flatten_dict(result, self.separator)

        result = ConfigReadResult(result, key=key, separator=self.separator)

        return result

    def write(self, key, value, read_existing_data=True):

        key, value = BaseConfigFile._validate_write_args(key, value)

        data = {}

        if read_existing_data and os.path.exists(self.name):
            data = self.read(flatten=False).data

        for k, v in zip(key, value):
            dpath.util.new(data, k, v, separator=".")

        with open(self.name, "w") as f:
            f.write(json.dumps(data, indent=4))
