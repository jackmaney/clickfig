from __future__ import absolute_import

import sys

sys.path = ['..', '.'] + sys.path

import unittest
import clickfig
# noinspection PyUnresolvedReferences
from dict_equal import dict_equal

cfg = clickfig.config.file.PythonConfigFile("./py/_test.py")


class TestPyRead(unittest.TestCase):
    def test_read(self):
        expected = {
            "x": 42,
            "foo": "bar",
            "square": lambda x: x ** 2
        }

        received = cfg.read().data

        self.assertEqual(set(expected.keys()), set(received.keys()))
        self.assertTrue(dict_equal(
            {k: v for k, v in expected.items() if k in ["x", "foo"]},
            {k: v for k, v in received.items() if k in ["x", "foo"]}
        ))

        for i in range(10):
            self.assertEqual(expected["square"](i), received["square"](i))
