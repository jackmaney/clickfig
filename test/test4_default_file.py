from __future__ import absolute_import
import sys

sys.path = ['..', '.'] + sys.path

import unittest
import clickfig
import os
from dict_equal import dict_equal


class TestDefaultFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg_ini = clickfig.config.file.INIConfigFile("./default_test.ini", default_file="./ini/default.ini",
                                                         verbose=False)
        cls.cfg_json = clickfig.config.file.JSONConfigFile("./default_test.json", default_file="./json/default.json",
                                                           verbose=False)

    def test_ini(self):
        expected = {
            "first": {
                "foo": "bar",
                "baz": "3"
            },
            "second": {
                "blarg": "something something\nsomething"
            }
        }

        self.assertTrue(self.cfg_ini.exists())
        self.assertTrue(dict_equal(self.cfg_ini.read(flatten=False).data, expected))

    def test_json(self):
        expected = {
            "first": {
                "foo": "bar",
                "baz": 3
            },
            "second": {
                "blarg": "something something\nsomething"
            }
        }

        self.assertTrue(self.cfg_json.exists())
        self.assertTrue(dict_equal(self.cfg_json.read(flatten=False).data, expected))

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.cfg_ini.name)
        os.unlink(cls.cfg_json.name)
