__config_types__ = [
    "ini",
    "json"
]


def dict_dfs(dictionary):
    result = {}
    for key, value in dictionary.items():
        if not isinstance(value, dict):
            result[key] = value
        else:
            result.update(dict_dfs({"{}.{}".format(key, x): y for x, y in value.items()}))

    return result
