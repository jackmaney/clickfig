
def dict_equal(first, second):
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
