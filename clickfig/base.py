import dpath

from .exception import KeyNotFoundException

__config_types__ = [
    "ini",
    "json"
]


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in earlier dicts.

    Modified from http://stackoverflow.com/a/26853961/554546
    :param list[dict] dict_args: An iterable of dictionaries.
    :return: A dictionary merged as above.
    :rtype: dict
    """
    result = {}
    for dictionary in reversed(dict_args):
        result.update(dictionary)
    return result


def return_key_value(data, key=None):
    """

    :param list[dict]|dict data: The data to be searched.
    :param str|None key: The key
    :return:
    """
    if data is None:
        return None

    if not isinstance(data, (list, tuple)):
        data = [data]

    data = merge_dicts(*data)

    if key is None:
        return data
    else:
        try:
            return dpath.util.get(data, key, separator=".")
        except KeyError:
            # Note: dpath will raise this error if the
            # path is valid, but the corresponding value is None
            # see: https://github.com/akesterson/dpath-python/issues/43
            # So, we work around this by going up a level and seeing if
            # the key actually exists. If it does, we return None.

            # To do this efficiently, we just flatten the dictionary
            # that we get from data and see if key is in it.

            flattened_data = flatten_dict(data)
            if key in flattened_data:
                return None

            # If we couldn't find the key in the flattened dictionary,
            # then we raise an exception indicating that the key wasn't found.
            raise KeyNotFoundException(key)


def flatten_dict(dictionary, separator="."):
    result = {}
    for key, value in dictionary.items():
        if not isinstance(value, dict):
            result[key] = value
        else:
            result.update(flatten_dict({"{}{}{}".format(key, separator, x): y
                                        for x, y in value.items()
                                        }))

    return result


def unflatten_dict(dictionary, separator="."):
    if any([k for k, v in dictionary.items() if isinstance(v, dict)]):
        raise ValueError(
            "Dictionary not flattened by separator '{}':\n{}".format(separator, dictionary))

    result = {}

    for key, value in dictionary.items():
        dpath.util.new(result, key, value, separator=separator)

    return result
