# pylint: disable=missing-docstring
import unittest

from src.validation import (
    get_python_type,
    validate_dict_keys,
    get_required_sections,
    get_required_keys,
    get_remaining_key_types,
    validate_key_types
)

class TestValidation(unittest.TestCase):
    def test_get_python_type(self):
        self.assertEqual(get_python_type('str'), str)
        self.assertEqual(get_python_type('string'), str)
        self.assertEqual(get_python_type('int'), int)
        self.assertEqual(get_python_type('bool'), bool)
        self.assertEqual(get_python_type('boolean'), bool)
        self.assertEqual(get_python_type('float'), float)
        self.assertEqual(get_python_type('list'), list)
        self.assertEqual(get_python_type('array'), list)
        self.assertEqual(get_python_type('dict'), dict)
        self.assertEqual(get_python_type(None), None)

    def test_validate_dict_keys_valid(self):
        dict_value = {
            'key0': 'value0',
            'key1': 'value1',
            'key2': 'value2',
        }
        # This should not raise an exception
        validate_dict_keys(dict_value)

    def test_validate_dict_keys_invalid(self):
        dict_value = {
            'key0': 'value0',
            1: 'value1',
            'key2': 'value2',
        }
        with self.assertRaises(TypeError):
            validate_dict_keys(dict_value)

    def test_get_required_sections(self):
        schema = {
            'section0': {
                'required': True,
                'keys': {
                    'key0': {'type': 'str'},
                    'key1': {'type': 'int'},
                }
            },
            'section1': {
                'required': False,
                'keys': {
                    'key2': {'type': 'bool'},
                    'key3': {'type': 'float'},
                }
            }
        }
        expected_required_sections = ['section0']
        actual_required_sections = get_required_sections(schema)
        self.assertEqual(actual_required_sections, expected_required_sections)


    def test_get_required_sections_no_required_sections(self):
        schema = {
            'section0': {
                'required': False,
                'keys': {
                    'key0': {'type': 'str'},
                    'key1': {'type': 'int'},
                }
            },
            'section1': {
                'required': False,
                'keys': {
                    'key2': {'type': 'bool'},
                    'key3': {'type': 'float'},
                }
            }
        }
        expected_required_sections = []
        actual_required_sections = get_required_sections(schema)
        self.assertEqual(actual_required_sections, expected_required_sections)

    def test_get_required_keys_section(self):
        section_definition = {
            'keys': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
                'key2': {'type': 'bool', 'required': False},
                'key3': {'type': 'float'},
            }
        }
        expected_required_keys = [
            ('key0', str),
            ('key1', int),
        ]
        actual_required_keys = get_required_keys(section_definition)
        self.assertEqual(actual_required_keys, expected_required_keys)

    def test_get_required_keys_entry(self):
        section_definition = {
            'entry': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
                'key2': {'type': 'bool', 'required': False},
                'key3': {'type': 'float'},
            }
        }
        expected_required_keys = [
            ('key0', str),
            ('key1', int),
        ]
        actual_required_keys = get_required_keys(section_definition, entry=True)
        self.assertEqual(actual_required_keys, expected_required_keys)

    def test_get_remaining_key_types(self):
        reference_key_schema = {
            'key0': {'type': 'str'},
            'key1': {'type': 'int'},
            'key2': {'type': 'bool'},
            'key3': {'type': 'float'},
        }
        verified_keys = ['key0', 'key1']
        expected_remaining_key_types = [
            ('key2', bool),
            ('key3', float),
        ]
        actual_remaining_key_types = get_remaining_key_types(
            reference_key_schema, verified_keys
        )
        # Compare both lists, they should be of same length and have the same elements
        self.assertEqual(len(actual_remaining_key_types), len(expected_remaining_key_types))
        for i,j in enumerate(actual_remaining_key_types):
            self.assertIn(j, expected_remaining_key_types)
        for i,j in enumerate(expected_remaining_key_types):
            self.assertIn(j, actual_remaining_key_types)

    def test_validate_key_types(self):
        key_types = [
            ('key0', str),
            ('key1', int),
            ('key2', bool),
            ('key3', float),
        ]
        keys_dict = {
            'key0': 'value0',
            'key1': 1,
            'key2': True,
            'key3': 3.14,
        }
        validate_key_types(key_types, keys_dict)

    def test_validate_required_key_types(self):
        required_keys = [
            ('key0', str),
            ('key1', int),
            ('key2', bool),
            ('key3', float),
        ]
        section = {
            'key0': 'value0',
            'key1': 1,
            'key2': True,
            'key3': 3.14,
        }
        validate_key_types(required_keys, section, required=True)
