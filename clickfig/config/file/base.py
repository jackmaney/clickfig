import os
import shutil
import tempfile
from abc import ABCMeta, abstractmethod

from six import PY2

from clickfig.base import flatten_dict, __config_types__

if PY2:
    FileNotFoundError = IOError


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


class BaseConfigFile(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, level="__default__",
                 default_file=None, separator=".", verbose=True):

        self.name = name
        self.level = level
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

    @classmethod
    def temp_clone(cls, name, base_file):

        kwargs = {k: getattr(base_file, k)
                  for k in ["level", "default_file", "separator",
                            "verbose"]}

        return cls(name=name, **kwargs)

    def unset(self, key):
        config_data = flatten_dict(self.read().data)

        del config_data[key]

        with tempfile.NamedTemporaryFile() as temp:
            tmp_config = self.__class__.temp_clone(name=temp.name, base_file=self)

            key = [x for x in config_data.keys()]
            value = [config_data[x] for x in key]

            tmp_config.write(key=key, value=value, read_existing_data=False)

            shutil.copyfile(temp.name, self.name)

    @abstractmethod
    def read(self, key=None, flatten=True):
        pass

    @staticmethod
    def _validate_write_args(key, value):

        if not isinstance(key, (list, tuple)):
            key = [key]

        if not isinstance(value, (list, tuple)):
            value = [value]

        if len(value) != len(key):
            raise ValueError("Number of keys and values do not match ({} vs {})".format(
                len(key), len(value)
            ))

        return key, value

    @abstractmethod
    def write(self, key, value):
        pass

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
