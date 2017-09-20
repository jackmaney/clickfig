def dict_equal(first, second):
    """
    This is a utility function used in testing to determine if two dictionaries are, in a nested sense, equal (ie they have the same keys and values at all levels).

    :param dict first: The first dictionary to compare.
    :param dict second: The second dictionary to compare.
    :return: Whether or not the dictionaries are (recursively) equal.
    :rtype: bool
    """
    if not set(first.keys()) == set(second.keys()):
        return False

    for k1, v1 in first.items():
        if isinstance(v1, dict) and isinstance(second[k1], dict):
            if not dict_equal(v1, second[k1]):
                return False
        elif not isinstance(v1, dict) and not isinstance(second[k1], dict):
            if v1 != second[k1]:
                return False
        else:
            return False

    return True
