import json
from warnings import warn

import six.moves as sm
import click
import os
import sys
import traceback


# Compatibility with Python 2 and 3
try:
    OSError
except NameError:
    OSError = IOError

__all__ = ["read"]

__config_types__ = [
    "ini",
    "json"
]


def read(config_file, config_type="ini", config_dir=None, app_name=None,
         **kwargs):
    """
    Reads the configuration file.

    :param str config_file: The name of the configuration file **without** the path.
    :param str config_type: The type of configuration file.
    Currently, only ``"ini"`` (via :py:`configparser`) and ``"json"`` are supported.
    :param str config_dir: The name of the directory in which the configuration file resides.
    If unset, then it will be found via `click's get_app_dir utility <http://click.pocoo.org/4/api/#click.get_app_dir>`_.
    :param str app_name: If this parameter is set and ``config_dir`` is not,
    then this will be used to find ``config_dir``.
    :param dict kwargs: Parameters to pass into `click.get_app_dir. <http://click.pocoo.org/4/api/#click.get_app_dir>`_.
    :return: A dictionary representing the structure of the configuration file.
    :rtype: dict
    """

    result = None

    if config_type == "ini":
        result = _read_ini(config_file,
                           config_dir=config_dir, app_name=app_name, **kwargs)
    elif config_type == "json":
        result = _read_json(config_file,
                            config_dir=config_dir, app_name=app_name, **kwargs)

    return result


def get_config_file(f):
    """
    A decorator that takes care of the following common actions among all readers:

    If the ``config_dir`` named parameter is not set, then it is set via
    `click's get_app_dir utility <http://click.pocoo.org/4/api/#click.get_app_dir>`_
    and the ``app_name`` parameter, if set (a :py:`ValueError` is thrown if ``app_name``
    and ``config_dir`` are both not set).

    .. note::

        This decorator assumes that there is only one positional argument for ``f``.

    """

    def wrap(config_file, **kwargs):
        config_dir = kwargs.get("config_dir")
        app_name = kwargs.get("app_name")

        if config_dir is None and app_name is None:
            raise ValueError(
                "One of 'config_dir' or 'app_name' must be set!")

        roaming = kwargs.get("roaming", True)
        force_posix = kwargs.get("force_posix", True)

        config_dir = config_dir or click.get_app_dir(app_name,
                                                     roaming=roaming,
                                                     force_posix=force_posix)

        kwargs["config_dir"] = config_dir

        return f(config_file, **kwargs)

    return wrap


@get_config_file
def _read_ini(config_file, config_dir=None, app_name=None, **kwargs):
    """
    Reads .ini configuration files.

    :param str config_file: The name of the configuration file **without** the path.
    :param str config_dir: The name of the directory in which the configuration file resides.
    If unset, then it will be found via `click's get_app_dir utility <http://click.pocoo.org/4/api/#click.get_app_dir>`_.
    :param str app_name: If this parameter is set and ``config_dir`` is not,
    then this will be used to find ``config_dir``.
    :param dict kwargs: Parameters to pass into `click.get_app_dir. <http://click.pocoo.org/4/api/#click.get_app_dir>`_.
    :return: A dictionary, mapping each section name to a dictionary of key-value pairs for that section.
    :rtype: dict
    """
    cfg = sm.configparser.ConfigParser()
    cfg.read(os.path.join(config_dir, config_file))
    return {section: dict(cfg[section]) for section in cfg.sections()} or None


@get_config_file
def _read_json(config_file, config_dir=None, app_name=None, **kwargs):
    """
    Reads .json configuration files.

    :param str config_file: The name of the configuration file **without** the path.
    :param str config_dir: The name of the directory in which the configuration file resides.
    If unset, then it will be found via `click's get_app_dir utility <http://click.pocoo.org/4/api/#click.get_app_dir>`_.
    :param str app_name: If this parameter is set and ``config_dir`` is not,
    then this will be used to find ``config_dir``.
    :param dict kwargs: Parameters to pass into `click.get_app_dir. <http://click.pocoo.org/4/api/#click.get_app_dir>`_.
    :return: Whatever data structure is parsed from the file via :py:`json` (usually a ``dict``).
    """

    result = None
    full_config_file = os.path.join(config_dir, config_file)

    try:
        with open(full_config_file) as f:
            json_blob = f.read()
            try:
                result = json.loads(json_blob)
            except ValueError:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
                warn("The file {} does not appear to be valid JSON".format(full_config_file))
    except OSError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=5, file=sys.stdout)
        warn("There was a problem opening the file {}".format(
            os.path.join(config_dir, config_file)))

    return result
