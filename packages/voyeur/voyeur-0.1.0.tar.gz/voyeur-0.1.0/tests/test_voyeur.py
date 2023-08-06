# coding=utf-8
"""
Copyright 2013, Gilles Devaux.

All rights reserved.

"""
import unittest

from voyeur import view
from voyeur.types import DeferredType


class TestVoyeur(unittest.TestCase):
    def test_types(self):
        definition = {
            'int': int,
            'str': str
        }
        data = {
            'int': '1',
            'str': 'string'
        }
        result = view(data, definition)
        self.assertDictEqual({'int': 1, 'str': 'string'},
                             result)

    def test_object_input(self):
        definition = {
            'int': int,
            'str': str
        }

        class TestObject(object):
            int = 1

            @property
            def str(self):
                return 'string'

        result = view(TestObject(), definition)
        self.assertDictEqual({'int': 1, 'str': 'string'},
                             result)

    def test_kwargs(self):
        def mystring(value, test=None):
            return "%s:test:%s" % (value, test)

        definition = {
            'int': int,
            'str': mystring
        }
        data = {
            'int': '1',
            'str': 'string'
        }
        result = view(data, definition, test='argh')
        self.assertDictEqual({'int': 1, 'str': 'string:test:argh'}, result)

    def test_list(self):
        definition = {
            'int': int,
            'str': str
        }
        data = [{'int': '1', 'str': 'string'},
                {'int': '2', 'str': 'string2'}]
        result = view(data, definition)
        self.assertListEqual([{'int': 1, 'str': 'string'},
                              {'int': 2, 'str': 'string2'}],
                             result)

    def test_nested(self):
        definition = {
            'int': int,
            'nested': {'n1': int}
        }
        data = {'int': '1', 'nested': {'n1': '2'}}
        result = view(data, definition)
        self.assertDictEqual({'int': 1, 'nested': {'n1': 2}}, result)

    def test_nested_list(self):
        definition = {
            'int': int,
            'nested': {'n1': int}
        }
        data = {'int': '1', 'nested': [{'n1': '2'}, {'n1': '3'}]}
        result = view(data, definition)
        self.assertDictEqual({'int': 1, 'nested': [{'n1': 2}, {'n1': 3}]}, result)

    def test_complex_type(self):
        definition = {
            'int': int,
            'computed': DeferredType('int', int)
        }
        data = {'int': '1'}
        result = view(data, definition)
        self.assertDictEqual({'int': 1, 'computed': 1}, result)

    def test_complex_type_with_kwargs(self):
        def mystring(value, test=None):
            return "%s:test:%s" % (value, test)

        definition = {
            'int': int,
            'computed_no_callable': DeferredType('int'),
            'computed_simple': DeferredType('int', int),
            'computed': DeferredType('int', mystring)
        }
        data = {'int': '1'}
        result = view(data, definition, test='argh')
        self.assertDictEqual({'int': 1, 'computed_no_callable': '1', 'computed_simple': 1, 'computed': '1:test:argh'}, result)
