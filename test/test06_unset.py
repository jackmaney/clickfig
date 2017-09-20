from __future__ import absolute_import
import sys

sys.path = ['..', '.'] + sys.path

import unittest
import clickfig
from clickfig import exception

import os

cfg_ini = clickfig.Config([{"name": "./default_test_unset.ini", "default": "./ini/default.ini"}],
                          verbose=False)
cfg_json = clickfig.Config([{"name": "./default_test_unset.json", "default": "./json/default.json"}],
                           verbose=True)


class TestUnset(unittest.TestCase):
    def test_ini(self):
        cfg_ini.unset("first.foo")

        with self.assertRaises(exception.KeyNotFoundException):
            cfg_ini.read(key="first.foo")

    def test_json(self):

        cfg_json.unset("second.blarg")

        with self.assertRaises(exception.KeyNotFoundException):
            cfg_json.read("key=second.blarg")

    @classmethod
    def tearDownClass(cls):
        os.unlink(cfg_ini.config_files[0].name)
        os.unlink(cfg_json.config_files[0].name)
