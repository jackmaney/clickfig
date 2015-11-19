import json
import os

import click
import dpath.util
import six.moves as sm

from .base import __config_types__


def _return_key_value(data, key=None):
    if data is None:
        return None

    if key is None:
        return data
    else:
        try:
            return dpath.util.get(data, key, separator=".")
        except (KeyError, ValueError):
            return None


class ConfigFile(object):
    def __init__(self, config_file, config_type="ini",
                 config_dir=None, app_name=None, default_file=None,
                 dir_options=None, verbose=False):

        if config_type not in __config_types__:
            raise ValueError("Invalid config_type: {} (must be one of {})".format(
                config_type, ",".join(__config_types__)
            ))

        dir_options = dir_options or {}

        self.config_type = config_type
        self.app_name = app_name
        self.default_file = default_file
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

    def exists(self):

        return os.path.join(self.config_file)

    def read(self, key=None):

        method_name = "_read_{}".format(self.config_type)

        return getattr(self, method_name)(key=key)

    def _read_ini(self, key=None):

        if not self.exists():
            return None

        cfg = sm.configparser.ConfigParser()
        cfg.read(self.config_file)
        data = {section: dict(cfg[section]) for section in cfg.sections()} or None

        return _return_key_value(data, key=key)

    def _read_json(self, key=None):

        if not self.exists():
            return None

        with open(self.config_file) as f:
            data = json.loads(f.read())

        return _return_key_value(data, key=key)

    def write(self, key, value):

        method_name = "_write_{}".format(self.config_type)

        return getattr(self, method_name)(key, value)

    def _write_ini(self, key, value):

        if len(key.split(".")) != 2:
            raise ValueError("For .ini files, keys must be of the form section.option")

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
            data = self._read_json()

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
