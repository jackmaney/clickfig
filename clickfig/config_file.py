import json
import os

import click
import dpath.util
import six.moves as sm

from .base import __config_types__, return_key_value, flatten_dict


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

        if isinstance(self.data, dict):

            if self.key is None:

                result = "\n".join(["{}={}".format(k, v)
                                    for k, v in flatten_dict(self.data, self.separator).items()])
            else:

                result = "\n".join(["{}{}{}={}".format(self.key, self.separator, k, v)
                                    for k, v in flatten_dict(self.data, self.separator).items()])

        else:
            result = str(self.data)

        return result


class ConfigFile(object):
    def __init__(self, config_file, config_type="ini",
                 config_dir=None, app_name=None, default_file=None,
                 dir_options=None, separator=".", verbose=True):

        if config_type not in __config_types__:
            raise ValueError("Invalid config_type: {} (must be one of {})".format(
                config_type, ",".join(__config_types__)
            ))

        dir_options = dir_options or {}

        self.config_type = config_type
        self.app_name = app_name
        self.default_file = default_file
        self.separator = separator
        self.verbose = verbose

        if config_file != os.path.basename(config_file) and config_dir is None:
            config_file = os.path.abspath(os.path.expanduser(config_file))
            self.config_dir, self.config_file = \
                (os.path.dirname(config_file), os.path.basename(config_file))

        if self.config_dir is None and self.app_name is None:
            raise ValueError(
                "One of 'config_dir' or 'app_name' must be set for a config_file of {}".format(
                    self.config_file
                ))

        self.config_dir = self.config_dir or \
                          click.get_app_dir(app_name, roaming=dir_options.get("roaming", True),
                                            force_posix=dir_options.get("force_posix", False))

        self.config_file = os.path.join(config_dir, config_file)

        if not self.exists():
            if not os.path.exists(self.default_file):
                raise FileNotFoundError(
                    "Configuration file {} not found, and no default config file specified.".format(
                        self.config_file
                    ))
            else:
                self.write_from_default()

    def exists(self):

        return os.path.exists(self.config_file)

    def read(self, key=None, flatten=True):

        method_name = "_read_{}".format(self.config_type)

        return ConfigReadResult(getattr(self, method_name)(key=key, flatten=flatten),
                                key=key, separator=self.separator)

    def _read_ini(self, key=None, flatten=True):

        if not self.exists():
            return None

        cfg = sm.configparser.ConfigParser()
        cfg.read(self.config_file)
        data = {section: dict(cfg[section]) for section in cfg.sections()} or None

        result = return_key_value(data, key=key)

        if flatten and isinstance(result, dict):
            result = flatten_dict(result, self.separator)

        return result

    def _read_json(self, key=None, flatten=True):

        if not self.exists():
            return None

        with open(self.config_file) as f:
            data = json.loads(f.read())

        result = return_key_value(data, key=key)

        if flatten and isinstance(result, dict):
            result = flatten_dict(result, self.separator)

        return result

    def write(self, key, value):

        method_name = "_write_{}".format(self.config_type)

        return getattr(self, method_name)(key, value)

    def _write_ini(self, key, value):

        if not key or len(key.split(self.separator)) > 2:
            raise ValueError(
                "For .ini files, keys must be a top-level section or of the form section{}option".format(
                    self.separator
                ))

        section, option = key.split(".")

        cfg = sm.configparser.ConfigParser()

        if os.path.exists(self.config_file):
            cfg.read(self.config_file)

        if section not in cfg:
            cfg[section] = {}

        cfg[section][option] = str(value)

        with open(self.config_file, "w") as f:
            cfg.write(f)

    def _write_json(self, key, value):

        data = {}

        if os.path.exists(self.config_file):
            data = self.read(flatten=False).data

        dpath.util.new(data, key, value, separator=".")

        with open(self.config_file, "w") as f:
            f.write(json.dumps(data, indent=4))

    def write_from_default(self):

        if not self.default_file:
            return

        with open(self.default_file) as f:
            config_data = f.read()

        if self.verbose:
            print("Creating default config file at {}".format(self.config_file))

        with open(self.config_file, "w") as f:
            f.write(config_data)
