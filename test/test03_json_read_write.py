from __future__ import absolute_import
import shutil
import sys

sys.path = ['..', '.'] + sys.path

import unittest
import clickfig
# noinspection PyUnresolvedReferences
from dict_equal import dict_equal

cfg = clickfig.config.file.JSONConfigFile("./json/test.json")


class TestJSONReadWrite(unittest.TestCase):

    def setUpClass(cls):
        shutil.copyfile("./json/test.json", "./json/test.json.bak")

    def tearDownClass(cls):
        shutil.move("./json/test.json.bak", "./json/test.json")

    def test_read(self):
        expected = {
            "bar.meh.a": 1,
            "bar.meh.b": 2,
            "bar.meh.c": 3,
            "bar.blah": "blarg",
            "foo": "baz",
            "q": None
        }

        self.assertTrue(dict_equal(cfg.read().data, expected))

    def test_read_key(self):

        self.assertEqual(cfg.read(key="bar.blah").data, "blarg")

        self.assertTrue(dict_equal(cfg.read(key="bar.meh").data,
                                   {"a": 1, "b": 2, "c": 3}))
        self.assertTrue(cfg.read(key="q").data is None)

    def test_write(self):

        cfg.write("bar.blah", "something")
        self.assertEqual(cfg.read(key="bar.blah").data, "something")

        cfg.write("bar.meh.a", 12)
        self.assertEqual(cfg.read(key="bar.meh.a").data, 12)

        # Undo what we've done so that we can reproduce this test!
        cfg.write("bar.blah", "blarg")
        cfg.write("bar.meh.a", 1)
        self.assertEqual(cfg.read(key="bar.blah").data, "blarg")
        self.assertEqual(cfg.read(key="bar.meh.a").data, 1)
