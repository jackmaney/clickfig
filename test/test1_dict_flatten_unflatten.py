import sys

sys.path = ['..'] + sys.path

import unittest
import dpath.util
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


class TestDictFlattenUnflatten(unittest.TestCase):
    def test_flatten(self):
        flattened = flatten_dict(dict_unflat)
        self.assertFalse(any([isinstance(v, dict) for k, v in flattened.items()]))
        self.assertEqual(sorted([flattened.items()]), sorted([dict_flat.items()]))

    def test_unflatten(self):
        unflattened = unflatten_dict(dict_flat)

        self.assertEqual(set(unflattened.keys()), {"a", "one", "two", "list"})

        self.assertTrue(all([unflattened[k] == dict_unflat[k]
                             for k in ["a", "one", "two", "list"]]))

        self.assertEqual([x for x in unflattened["a"].keys()], ["b"])
        self.assertEqual(set(dpath.util.get(unflattened, "a/b").keys()), {"c", "d", "z", "e"})
        self.assertEqual(
            set(dpath.util.get(unflattened, "a/b/e").items()),
            set(dpath.util.get(dict_unflat, "a/b/e").items())
        )
        self.assertEqual(
            set(dpath.util.search(unflattened, "a/b/[cdz]")),
            set(dpath.util.search(dict_unflat, "a/b/[cdz]"))
        )
