import sys

sys.path = ['..'] + sys.path

import unittest
from clickfig.base import flatten_dict, unflatten_dict

dict_flat = {
    "a.b.c": "foo",
    "a.b.d": "bar",
    "a.b.z": "baz",
    "a.b.e.f": 2,
    "one": 1,
    "two": 2,
    "list": ["of", "some", "things", 1, 2, 3]
}

dict_unflat = {
    "a": {
        "b": {
            "c": "foo",
            "d": "bar",
            "z": "baz",
            "e": {"f": 2}
        }
    },
    "one": 1,
    "two": 2,
    "list": ["of", "some", "things", 1, 2, 3]
}


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


class TestDictFlattenUnflatten(unittest.TestCase):
    def test_equal(self):
        d1 = {"a": 2, "b": {"c": 3}}
        d2 = {"a": 2, "b": 3}
        d3 = {"a": 2, "c": 8}
        d4 = {"b": {"c": 4}, "a": 2}
        d5 = {"b": {"c": 3}, "a": 2}

        self.assertFalse(dict_equal(d1, d2))
        self.assertFalse(dict_equal(d1, d3))
        self.assertFalse(dict_equal(d1, d4))
        self.assertTrue(dict_equal(d1, d5))

    def test_flatten(self):
        self.assertTrue(dict_equal(flatten_dict(dict_unflat), dict_flat))

    def test_unflatten(self):
        self.assertTrue(dict_equal(unflatten_dict(dict_flat), dict_unflat))
