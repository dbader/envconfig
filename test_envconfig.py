# coding=utf8

"""Unit tests for the config module."""

# Silence "missing docstring", "method could be a function", and
# "too many public methods" messages:
# pylint: disable-msg=R0201,C0111,R0904

import unittest
import os
import envconfig


class TestConfig(unittest.TestCase):
    def assert_get_set_bool(self, value, expected_value):
        os.environ['TEST_BOOLEAN_VALUE'] = value
        self.assertEqual(envconfig.bool('TEST_BOOLEAN_VALUE'), expected_value)

    def test_getstr(self):
        os.environ['TEST_VALUE_STR'] = 'Hello, World'
        self.assertEqual(envconfig.str('TEST_VALUE_STR'), 'Hello, World')

    def test_getstr_strip_whitespace(self):
        os.environ['TEST_VALUE_STR'] = '  hello  '
        self.assertEqual(envconfig.str('TEST_VALUE_STR'), 'hello')

    def test_getint(self):
        os.environ['TEST_VALUE_INT'] = '12345'
        self.assertEqual(envconfig.int('TEST_VALUE_INT'), 12345)

    def test_getbool(self):
        self.assert_get_set_bool('yes', True)
        self.assert_get_set_bool('1', True)
        self.assert_get_set_bool('YeS', True)
        self.assert_get_set_bool('True', True)
        self.assert_get_set_bool('true', True)
        self.assert_get_set_bool(' 1 ', True)
        self.assert_get_set_bool('YES\t', True)
        self.assert_get_set_bool('\tYES\t', True)
        self.assert_get_set_bool('false', False)
        self.assert_get_set_bool('no', False)
        self.assert_get_set_bool('0', False)
        self.assert_get_set_bool('  NO  ', False)

    def test_getinvalid(self):
        if 'DOES_NOT_EXIST' in os.environ:
            del os.environ['DOES_NOT_EXIST']
        self.assertRaises(KeyError, lambda: envconfig.str('DOES_NOT_EXIST'))

    def test_invalid_bool(self):
        os.environ['INVALID_BOOL'] = 'nope'
        self.assertRaises(ValueError, lambda: envconfig.bool('INVALID_BOOL'))

    def test_getlist(self):
        os.environ['LIST_TEST'] = 'one,two, three ,four '
        self.assertEqual(envconfig.list('LIST_TEST'),
                         ['one', 'two', 'three', 'four'])
        os.environ['LIST_TEST'] = 'one#two# three #four '
        self.assertEqual(envconfig.list('LIST_TEST', separator='#'),
                         ['one', 'two', 'three', 'four'])
        os.environ['LIST_TEST'] = ''
        self.assertEqual(envconfig.list('LIST_TEST'), [])

    def test_getdict(self):
        os.environ['DICT_TEST'] = 'key1:val1,key2:val2'
        self.assertEqual(envconfig.dict('DICT_TEST'),
                         {'key1': 'val1', 'key2': 'val2'})
        os.environ['DICT_TEST'] = 'key1  :  val1 , key2 : val2'
        self.assertEqual(envconfig.dict('DICT_TEST'),
                         {'key1': 'val1', 'key2': 'val2'})
        os.environ['DICT_TEST'] = 'key1#val1,key2#val2'
        self.assertEqual(envconfig.dict('DICT_TEST', key_value_separator="#"),
                         {'key1': 'val1', 'key2': 'val2'})
        os.environ['DICT_TEST'] = ''
        self.assertEqual(envconfig.dict('DICT_TEST'), {})
        os.environ['DICT_TEST'] = 'key1 val1 key2 val2'
        self.assertRaises(ValueError, lambda: envconfig.dict('DICT_TEST'))