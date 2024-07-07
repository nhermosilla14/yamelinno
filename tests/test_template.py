# pylint: disable=missing-docstring
"""
Tests for the templates module.
"""

import unittest
import os

from src.templates import load_config, deep_merge_dicts, validate_template

class TestTemplates(unittest.TestCase):

    def test_load_config_leaf_template(self):
        # Gen fake config file
        config_file = 'leaf_template.yaml'
        with open(config_file, 'w', encoding='utf-8') as file:
            file.write('key0: value1\nkey1: value2\nkey2: value3\n')

        expected_config = {
            'key0': 'value1',
            'key1': 'value2',
            'key2': 'value3'
        }
        actual_config = load_config(config_file)
        # Clean up
        os.remove(config_file)
        self.assertEqual(actual_config, expected_config)


    def test_load_config_parent_template(self):
        config_file = 'parent_template.yaml'
        with open(config_file, 'w', encoding='utf-8') as file:
            file.write('key0: value1\nkey1: value2\nkey2: value3\nkey3: value4\nkey4: value5\n')

        expected_config = {
            'key0': 'value1',
            'key1': 'value2',
            'key2': 'value3',
            'key3': 'value4',
            'key4': 'value5'
        }
        actual_config = load_config(config_file)
        # Clean up
        os.remove(config_file)
        self.assertEqual(actual_config, expected_config)


    def test_deep_merge_dicts(self):
        source = {
            'key0': 'value1',
            'key1': {
                'subkey0': 'subvalue1',
                'subkey1': 'subvalue2'
            }
        }
        destination = {
            'key1': {
                'subkey1': 'subvalue2',
                'subkey2': 'subvalue3'
            },
            'key2': 'value3'
        }
        expected_merged = {
            'key0': 'value1',
            'key1': {
                'subkey0': 'subvalue1',
                'subkey1': 'subvalue2',
                'subkey2': 'subvalue3'
            },
            'key2': 'value3'
        }
        actual_merged = deep_merge_dicts(source, destination)
        self.assertEqual(actual_merged, expected_merged)


    def test_validate_valid_template(self):
        template = {
            'key0': 'value1',
            'key1': 'value2',
            'key2': 'value3'
        }
        self.assertIsNone(validate_template(template))

    def test_validate_invalid_template(self):
        template = {
            'key0': 'value1',
            'key1': 'value2',
            2: 'value3'  # Invalid key type
        }
        with self.assertRaises(Exception):
            validate_template(template)

if __name__ == '__main__':
    unittest.main()
