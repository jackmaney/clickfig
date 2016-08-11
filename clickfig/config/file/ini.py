from collections import OrderedDict

import os
import six.moves as sm

from .base import BaseConfigFile, ConfigReadResult, flatten_dict

from ...base import return_key_value


class INIConfigFile(BaseConfigFile):

    def read(self, key=None, flatten=True):

        if not self.exists():
            return None

        cfg = sm.configparser.ConfigParser()
        cfg.read(self.name)
        data = OrderedDict([(section,
                             OrderedDict([(k, v) for k, v in cfg[section].items()])
                             )
                            for section in cfg.sections()
                            ]
                           ) or None

        result = return_key_value(data, key=key)

        if flatten and isinstance(result, dict):
            result = flatten_dict(result, self.separator)

        result = ConfigReadResult(result, key=key, separator=self.separator)

        return result

    def write(self, key, value, read_existing_data=True):

        key, value = BaseConfigFile._validate_write_args(key, value)

        cfg = sm.configparser.ConfigParser()

        if read_existing_data and os.path.exists(self.name):
            cfg.read(self.name)

        for k, v in zip(key, value):

            if not k or len(k.split(self.separator)) > 2:
                raise ValueError(
                    "For .ini files, keys must be a top-level section or of the form section{}option".format(
                        self.separator
                    ))

            section, option = k.split(".")

            if section not in cfg:
                cfg[section] = {}

            cfg[section][option] = str(v)

        with open(self.name, "w") as f:
            cfg.write(f)
