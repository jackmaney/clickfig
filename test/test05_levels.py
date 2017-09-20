from __future__ import absolute_import

import sys

sys.path = ['..', '.'] + sys.path

import unittest
import clickfig
from clickfig import exception

cfg_ini = clickfig.Config(
    [
        {"level": "local", "name": "./ini/test.ini"},
        {"level": "global", "name": "./ini/test_global.ini"}
    ]
)

cfg_json = clickfig.Config(
    [
        {"level": "local", "name": "./json/test.json"},
        {"level": "global", "name": "./json/test_global.json"}
    ]
)

cfg_python = clickfig.Config(
    [
        {"level": "local", "name": "./py/_test.py"},
        {"level": "global", "name": "./py/_test_global.py"}
    ]
)


class TestLevels(unittest.TestCase):
    def test_ini_read(self):
        self.assertEqual(cfg_ini.read(key="foo.bar").data, "baz")
        self.assertEqual(cfg_ini.config_files[1].read(key="foo.bar").data, "blarg")

        self.assertEqual(cfg_ini.read(key="baz.first").data, "1")
        self.assertEqual(cfg_ini.read(key="baz.second").data, "2")

        with self.assertRaises(exception.KeyNotFoundException):
            cfg_ini.config_files[0].read(key="baz.first")

    def test_ini_write(self):
        cfg_ini.write("foo.bar", "meh")

        self.assertEqual(cfg_ini.read(key="foo.bar").data, "meh")
        self.assertEqual(cfg_ini.config_files[0].read(key="foo.bar").data, "meh")
        self.assertEqual(cfg_ini.config_files[1].read(key="foo.bar").data, "blarg")

        cfg_ini.write("foo.bar", "baz")

        self.assertEqual(cfg_ini.read(key="foo.bar").data, "baz")
        self.assertEqual(cfg_ini.config_files[0].read(key="foo.bar").data, "baz")

        cfg_ini.write("baz.first", "17", level="global")
        self.assertEqual(cfg_ini.read(key="baz.first").data, "17")
        self.assertEqual(cfg_ini.config_files[1].read(key="baz.first").data, "17")
        with self.assertRaises(exception.KeyNotFoundException):
            cfg_ini.config_files[0].read(key="baz.first")

        cfg_ini.write("baz.first", "1", level="global")
        self.assertEqual(cfg_ini.read(key="baz.first").data, "1")
        self.assertEqual(cfg_ini.config_files[1].read(key="baz.first").data, "1")
        with self.assertRaises(exception.KeyNotFoundException):
            cfg_ini.config_files[0].read(key="baz.first")

    def test_json_read(self):
        self.assertTrue(cfg_json.read(key="q").data is None)
        self.assertEqual(cfg_json.read(key="bar.blah").data, "blarg")
        self.assertEqual(cfg_json.config_files[1].read(key="q").data, 2)

        self.assertEqual(cfg_json.read(key="x").data, "yz")

        with self.assertRaises(exception.KeyNotFoundException):
            cfg_json.config_files[0].read(key="x")

    def test_json_write(self):
        cfg_json.write("bar.meh.a", 0)
        self.assertEqual(cfg_json.read(key="bar.meh.a").data, 0)
        self.assertEqual(cfg_json.config_files[0].read(key="bar.meh.a").data, 0)
        with self.assertRaises(exception.KeyNotFoundException):
            cfg_json.config_files[1].read(key="bar.meh.a")

        cfg_json.write("bar.meh.a", 1)
        self.assertEqual(cfg_json.read(key="bar.meh.a").data, 1)
        self.assertEqual(cfg_json.config_files[0].read(key="bar.meh.a").data, 1)
        with self.assertRaises(exception.KeyNotFoundException):
            cfg_json.config_files[1].read(key="bar.meh.a")

        cfg_json.write("x", "abc", level="global")
        self.assertEqual(cfg_json.read(key="x").data, "abc")
        self.assertEqual(cfg_json.config_files[1].read(key="x").data, "abc")
        with self.assertRaises(exception.KeyNotFoundException):
            cfg_json.config_files[0].read(key="x")

        cfg_json.write("x", "yz", level="global")
        self.assertEqual(cfg_json.read(key="x").data, "yz")
        self.assertEqual(cfg_json.config_files[1].read(key="x").data, "yz")
        with self.assertRaises(exception.KeyNotFoundException):
            cfg_json.config_files[0].read(key="x")

    def test_py_read(self):
        self.assertEqual(cfg_python.read(key="x").data, 42)
        self.assertEqual(cfg_python.read(key="foo").data, "bar")
        self.assertEqual(cfg_python.config_files[1].read(key="x").data, -3)

        for i in range(10):
            self.assertEqual(cfg_python.read("square").data(i), i**2)

        self.assertTrue(cfg_python.read(key="q").data is None)

        with self.assertRaises(exception.KeyNotFoundException):
            cfg_python.config_files[0].read(key="q")

        with self.assertRaises(exception.KeyNotFoundException):
            cfg_python.config_files[1].read(key="square")