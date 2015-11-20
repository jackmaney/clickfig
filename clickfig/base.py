import dpath

__config_types__ = [
    "ini",
    "json"
]


def return_key_value(data, key=None):
    if data is None:
        return None

    if key is None:
        return data
    else:
        try:
            return dpath.util.get(data, key, separator=".")
        except (KeyError, ValueError):
            return None


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
