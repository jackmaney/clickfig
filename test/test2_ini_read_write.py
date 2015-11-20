import sys

sys.path = ['..', '.'] + sys.path

import unittest
import clickfig
from dict_equal import dict_equal

cfg = clickfig.ConfigFile("./ini/test.ini")


class TestIniReadWrite(unittest.TestCase):
    def test_read(self):
        expected = {
            "foo.bar": "baz",
            "foo.blah": "2",
            "section.stuff": "things",
            "section.other": "something else blah blah blah"
        }

        self.assertTrue(dict_equal(cfg.read().data, expected))

    def test_read_key(self):
        self.assertTrue(cfg.read(key="foo.bar"), "baz")
        self.assertTrue(
            dict_equal(cfg.read(key="section").data,
                       {
                           "stuff": "things",
                           "other": "something else blah blah blah"
                       }))

    def test_write(self):
        cfg.write("foo.bar", "meh")
        self.assertEqual(cfg.read(key="foo.bar").data, "meh")

        # Undo what we've done so that we can reproduce this test!
        cfg.write("foo.bar", "baz")
        self.assertTrue(cfg.read(key="foo.bar"), "baz")
