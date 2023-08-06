# -*- coding: utf-8 -*-


import unittest
import datetime

from pyramid.config import Configurator

from hapis import settings


class PyramidConfigTest(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()


class TestDottedOrString(PyramidConfigTest):
    def test_actual_dotted(self):
        dt_now1 = datetime.datetime.now
        dt_now2 = settings._dotted_or_string(
            self.config, 'datetime:datetime.now'
        )
        self.assertEqual(dt_now1, dt_now2)

    def test_nonstring(self):
        dt_now1 = datetime.datetime.now
        dt_now2 = settings._dotted_or_string(self.config, dt_now1)
        self.assertEqual(dt_now1, dt_now2)

    def test_not_dotted(self):
        not_a_dotted_name1 = 'not_a_dotted_name'
        not_a_dotted_name2 = settings._dotted_or_string(
            self.config, not_a_dotted_name1
        )
        self.assertEqual(not_a_dotted_name1, not_a_dotted_name2)


class TestMakeKvPair(unittest.TestCase):
    def test_one_eq_sign(self):
        parts1 = ('key', 'value')
        parts2 = settings._make_kv_pair('key = value')
        self.assertEqual(parts1, parts2)

    def test_two_eq_signs(self):
        parts1 = ('key', 'value = meaning')
        parts2 = settings._make_kv_pair('key = value = meaning')
        self.assertEqual(parts1, parts2)

    def test_no_eq_signs(self):
        self.assertRaises(
            ValueError, settings._make_kv_pair, 'key maps to value'
        )


class TestParseMultiline(PyramidConfigTest):
    def test_with_list(self):
        lines = ['not_a_dotted_name', 'datetime:datetime', datetime.datetime]
        lines1 = ['not_a_dotted_name', datetime.datetime, datetime.datetime]
        lines2 = settings.parse_multiline(self.config, lines)
        self.assertEqual(lines1, lines2)

    def test_with_string_of_mixed(self):
        lines = 'not_a_dotted_name\ndatetime:datetime\nalso not dotted\n'
        lines1 = ['not_a_dotted_name', datetime.datetime, 'also not dotted']
        lines2 = settings.parse_multiline(self.config, lines)
        self.assertEqual(lines1, lines2)

    def test_forbidden_dotted_with_list_of_mixed(self):
        lines = ['not_a_dotted_name', 'datetime:datetime', datetime.datetime]
        lines1 = ['not_a_dotted_name', 'datetime:datetime', datetime.datetime]
        lines2 = settings.parse_multiline(self.config, lines, dotted=False)
        self.assertEqual(lines1, lines2)

    def test_forbidden_dotted_with_string_of_mixed(self):
        lines = 'not_a_dotted_name\ndatetime:datetime\nalso not dotted\n'
        lines1 = ['not_a_dotted_name', 'datetime:datetime', 'also not dotted']
        lines2 = settings.parse_multiline(self.config, lines, dotted=False)
        self.assertEqual(lines1, lines2)


class TestParseKeyvaluePairs(PyramidConfigTest):
    def test_with_dict(self):
        kvs = {
            'key1': 'not_a_dotted_name',
            'key2': 'datetime:datetime',
            'key3': datetime.datetime,
        }
        kvs1 = {
            'key1': 'not_a_dotted_name',
            'key2': datetime.datetime,
            'key3': datetime.datetime,
        }
        kvs2 = settings.parse_keyvalue_pairs(self.config, kvs)
        self.assertEqual(kvs1, kvs2)

    def test_with_string_of_mixed(self):
        kvs = (
            'key1 = not_a_dotted_name\n'
            'key2 = datetime:datetime\n'
            'key3 = also not dotted\n'
        )
        kvs1 = {
            'key1': 'not_a_dotted_name',
            'key2': datetime.datetime,
            'key3': 'also not dotted',
        }
        kvs2 = settings.parse_keyvalue_pairs(self.config, kvs)
        self.assertEqual(kvs1, kvs2)

    def test_forbidden_dotted_with_list_of_mixed(self):
        kvs = {
            'key1': 'not_a_dotted_name',
            'key2': 'datetime:datetime',
            'key3': datetime.datetime,
        }
        kvs1 = {
            'key1': 'not_a_dotted_name',
            'key2': 'datetime:datetime',
            'key3': datetime.datetime,
        }
        kvs2 = settings.parse_keyvalue_pairs(self.config, kvs, dotted=False)
        self.assertEqual(kvs1, kvs2)

    def test_forbidden_dotted_with_string_of_mixed(self):
        kvs = (
            'key1 = not_a_dotted_name\n'
            'key2 = datetime:datetime\n'
            'key3 = also not dotted\n'
        )
        kvs1 = {
            'key1': 'not_a_dotted_name',
            'key2': 'datetime:datetime',
            'key3': 'also not dotted',
        }
        kvs2 = settings.parse_keyvalue_pairs(self.config, kvs, dotted=False)
        self.assertEqual(kvs1, kvs2)


class TestFilterByPrefix(unittest.TestCase):
    def test_prefix(self):
        in_dict = {
            'prefixed_key1': 1,
            'prefixed_key2': 2,
            'prefixed_key3': 'a',
            'another__key1': 3,
            'prefixed_key4': 'b',
            'another__key2': 'c',
        }
        out_dict1 = {
            'key1': 1,
            'key2': 2,
            'key3': 'a',
            'key4': 'b',
        }
        out_dict2 = settings.filter_by_prefix(in_dict, 'prefixed_')
        self.assertEqual(out_dict1, out_dict2)


class TestSplitKeys(unittest.TestCase):
    def test_default(self):
        in_dict = {
            'one.two.three.four': 4,
            'one.two.three.five': 5,
            'one.two.six': 6,
            'seven': 7,
            'eight.nine': 9,
            'nine.ten': 10,
            'eight.eleven': 11,
        }
        out_dict1 = {
            'one': {
                'two': {
                    'three': dict(four=4, five=5),
                    'six': 6,
                },
            },
            'seven': 7,
            'eight': dict(nine=9, eleven=11),
            'nine': dict(ten=10),
        }
        out_dict2 = settings.split_keys(in_dict)
        self.assertEqual(out_dict1, out_dict2)

    def test_separator(self):
        in_dict = {
            'one-two-three': 1,
            'one.two.three': 2,
            'one-two.three': 3,
        }
        out_dict1 = {
            'one': {
                'two': dict(three=1),
                'two.three': 3,
            },
            'one.two.three': 2,
        }
        out_dict2 = settings.split_keys(in_dict, separator='-')
        self.assertEqual(out_dict1, out_dict2)

    def test_maxsplit(self):
        in_dict = {
            'zero': 0,
            'one.two': 2,
            'one.three.four': 4,
            'one.three.five.six': 6,
        }
        out_dict1 = {
            'zero': 0,
            'one': {
                'two': 2,
                'three': {
                    'four': 4,
                    'five.six': 6,
                },
            },
        }
        out_dict2 = settings.split_keys(in_dict, maxsplit=2)
        self.assertEqual(out_dict1, out_dict2)
