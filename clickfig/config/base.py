import os

import click
import six

from clickfig.config.file import ConfigFile
from clickfig.exception import KeyNotFoundException


class Config(object):
    def __init__(self, file, app_name=None,
                 dir_options=None, separator=".", verbose=True):
        """
        :param str|list[dict[str,str]] file: Either a string denoting a single file or a list of dictionaries representing multiple files.
        Each such dict must have keys of ``name`` and ``level`` with an optional keys of ``default``, ``type``, and ``dir``.
        :param str app_name: Used to find locations of files if the full path is not provided.
        :param dir_options: Other options to pass into `click.get_app_dir <http://click.pocoo.org/api/#click.get_app_dir>`_.
        :param str separator: The separator to use for sections, subsections, etc in keys.
        :param bool verbose: Enable this if you want extra info...
        """

        if isinstance(file, six.string_types):
            self.file = [{"level": "__default__", "name": file}]
        else:
            for f in file:
                if "name" not in f and "level" not in f:
                    raise ValueError(
                            "File info {} doesn't contain required keys of 'name' and 'level".format(f)
                    )
                elif f.get("level") == "__default__":
                    raise ValueError("Invalid level name: __default__")

            self.file = file

        num_levels = len([f.get("level") for f in self.file])
        num_unique_levels = len(set(f.get("level") for f in self.file))
        if num_unique_levels != num_levels:
            raise ValueError("Levels must be distinct! "
                             "{} distinct levels vs {} total levels for files {}".
                             format(num_unique_levels, num_levels, self.file))

        self.separator = separator
        self.app_name = app_name
        self.verbose = verbose

        for f in self.file:
            if f.get("name") != os.path.basename(f.get("name")) and not f.get("dir"):
                f.setdefault("name", os.path.abspath(os.path.expanduser(f.get("name"))))
                f.setdefault("dir", os.path.dirname(f.get("name")))
                f.setdefault("name", os.path.basename(f.get("name")))

            if not f.get("dir") and self.app_name is None:
                raise ValueError("Cannot determine full path to config file {}. "
                                 "Please be more specific or specify app_name".format(f.get("name")))

            if not f.get("dir"):
                f_dir = click.get_app_dir(self.app_name, roaming=dir_options.get("roaming", True),
                                          force_posix=dir_options.get("force_posix", False))
                f.setdefault("dir", f_dir)

            f.setdefault("name", os.path.join(f.get("dir"), f.get("name")))

        self.config_files = [
            ConfigFile(f.get("name"), level=f.get("level", "__default__"),
                       type_=f.get("type"), default_file=f.get("default"),
                       separator=self.separator, verbose=self.verbose)
            for f in self.file]

    @property
    def levels(self):
        return [f.get("level") for f in self.file]

    @property
    def file_names(self):
        return [f.get("name") for f in self.file]

    def file_by_level(self, level):

        return [x for x in self.config_files if x.level == level][0]

    def read(self, key=None, flatten=True):
        if key is None:
            return [file.read(flatten=flatten) for file in self.config_files]
        else:
            for file in self.config_files:
                try:
                    return file.read(key=key, flatten=flatten)
                except KeyNotFoundException:
                    continue
            else:
                raise KeyNotFoundException(key)

    def write(self, key, value, level=None):

        if level is None and len(self.config_files) > 1:
            level = self.config_files[0].level

        level = level or "__default__"

        config_file = self.file_by_level(level)

        config_file.write(key, value)

    def unset(self, key, level=None):
        if level is None and len(self.config_files) > 1:
            level = self.config_files[0].level

        level = level or "__default__"

        config_file = self.file_by_level(level)

        config_file.unset(key)

