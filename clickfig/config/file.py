import json
import os
import shutil
import tempfile
from collections import OrderedDict

import dpath.util
import six.moves as sm
from six import PY2

if PY2:
    FileNotFoundError = IOError

from clickfig.base import __config_types__, return_key_value, flatten_dict


class ConfigReadResult(object):
    """
    This is a wrapper object around data returned by a ``ConfigFile.read`` call
    to handle the formatting of printed results. The data is stored in the ``data``
    attribute.
    """

    def __init__(self, data, key=None, separator="."):
        """
        Stores the data and keeps track of the separator for putting keys together (sections, subsections, etc).
        :param any data: The raw data passed in.
        :param str|None key: The key used to produce this data, if applicable.
        :param separator: The separator used to put parts of keys together.
        """
        self.data = data
        self.key = key
        self.separator = separator

    def __str__(self):
        """
        If the ``data`` attribute is a dictionary, then the paths are given along with their
        corresponding (non-dict) value, in the form "path=key". If ``data`` isn't a dict,
        then this just returns the string representation of the ``data``.
        """

        data_list = None

        if isinstance(self.data, dict):
            data_list = [self.data]

        if isinstance(self.data, (list, tuple)) and \
                all([isinstance(x, dict) for x in self.data]):
            data_list = self.data

        if data_list is None:
            result = str(self.data)

        elif self.key is None:

            result = "\n".join(["{}={}".format(k, v)
                                for d in data_list
                                for k, v in flatten_dict(d, self.separator).items()
                                ]
                               )
        else:

            result = "\n".join(["{}{}{}={}".format(self.key, self.separator, k, v)
                                for d in data_list
                                for k, v in flatten_dict(d, self.separator).items()
                                ]
                               )

        return result


class ConfigFile(object):
    def __init__(self, name, level="__default__",
                 type_=None, default_file=None, separator=".", verbose=True):

        if type_ is None:
            extension = name.split(".")[-1].lower()
            if extension in __config_types__:
                type_ = extension
            else:
                raise ValueError("Unable to determine the type of configuration file for {}. "
                                 "Please use the type_ parameter.".format(name))

        if type_ not in __config_types__:
            raise ValueError("Invalid configuration type: {} (must be one of {})".format(
                    type_, ",".join(__config_types__)
            ))

        self.name = name
        self.level = level
        self.type_ = type_
        self.default_file = default_file
        self.separator = separator
        self.verbose = verbose

        if not self.exists():
            if not os.path.exists(self.default_file):
                raise FileNotFoundError(
                        "Configuration file {} not found, and no default config file specified.".format(
                                self
                        ))
            else:
                self.write_from_default()

    def exists(self):

        return os.path.exists(self.name)

    def unset(self, key):

        config_data = flatten_dict(self.read().data)

        del config_data[key]

        with tempfile.NamedTemporaryFile() as temp:
            tmp_config = ConfigFile(name=temp.name, level=self.level,
                                    type_=self.type_, default_file=self.default_file,
                                    separator=self.separator, verbose=self.verbose)

            key = [x for x in config_data.keys()]
            value = [config_data[x] for x in key]

            tmp_config.write(key=key, value=value, read_existing_data=False)

            shutil.copyfile(temp.name, self.name)

    def read(self, key=None, flatten=True):

        method_name = "_read_{}".format(self.type_)

        return ConfigReadResult(getattr(self, method_name)(key=key, flatten=flatten),
                                key=key, separator=self.separator)

    def _read_ini(self, key=None, flatten=True):

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

        return result

    def _read_json(self, key=None, flatten=True):

        if not self.exists():
            return None

        with open(self.name) as f:
            data = json.loads(f.read(), object_pairs_hook=OrderedDict)

        result = return_key_value(data, key=key)

        if flatten and isinstance(result, dict):
            result = flatten_dict(result, self.separator)

        return result

    def write(self, key, value, read_existing_data=True):

        if not isinstance(key, (list, tuple)):
            key = [key]

        if not isinstance(value, (list, tuple)):
            value = [value]

        if len(value) != len(key):
            raise ValueError("Number of keys and values do not match ({} vs {})".format(
                    len(key), len(value)
            ))

        method_name = "_write_{}".format(self.type_)

        return getattr(self, method_name)(key, value, read_existing_data=read_existing_data)

    def _write_ini(self, key, value, read_existing_data=True):

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

    def _write_json(self, key, value, read_existing_data=True):

        data = {}

        if read_existing_data and os.path.exists(self.name):
            data = self.read(flatten=False).data

        for k, v in zip(key, value):
            dpath.util.new(data, k, v, separator=".")

        with open(self.name, "w") as f:
            f.write(json.dumps(data, indent=4))

    def write_from_default(self):

        if not self.default_file:
            return

        with open(self.default_file) as f:
            config_data = f.read()

        if self.verbose:
            print("Creating default config file at {}".format(self))

        with open(self.name, "w") as f:
            f.write(config_data)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __hash__(self):
        return hash(self.name)
