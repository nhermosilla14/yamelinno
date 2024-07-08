# pylint: disable=missing-docstring
"""
Tests for the templates module.
"""

import unittest
import os

from src.templates import (
    load_config,
    render_template,
    deep_merge_dicts,
    validate_template,
)


def compare_dicts(dict1, dict2, raise_error=False):
    """
    Compare two dictionaries to check if they have the same key-value pairs.

    Args:
        dict1 (dict): The first dictionary to compare.
        dict2 (dict): The second dictionary to compare.

    Returns:
        bool: True if the dictionaries have the same key-value pairs, False otherwise.
    """
    if len(dict1) != len(dict2):
        if raise_error:
            output_error = "".join([
                "The dictionaries do not have the same number of keys.\n",
                f"{dict1.keys()} != {dict2.keys()}"
            ])
            raise ValueError(output_error)
        return False
    for key, value in dict1.items():
        if isinstance(value, dict):
            if not compare_dicts(value, dict2[key]):
                if raise_error:
                    output_error = "".join([
                        f"Value for key {key} does not match.\n",
                        f"{value} != {dict2[key]}"
                    ])
                    raise ValueError(output_error)
                return False
        elif isinstance(value, list):
            if len(value) != len(dict2[key]):
                if raise_error:
                    output_error = "".join([
                        "The lists do not have the same number of items.\n",
                        f"{value} != {dict2[key]}"
                    ])
                    raise ValueError(output_error)
                return False
            # The order of the items in the list does not matter
            if not all(item in dict2[key] for item in value):
                if raise_error:
                    output_error = "".join([
                        "The lists do not have the same items.\n",
                        f"{value} != {dict2[key]}"
                    ])
                    raise ValueError(output_error)
                return False
        else:
            if value != dict2[key]:
                if raise_error:
                    output_error = "".join([
                        f"Value for key {key} does not match.\n",
                        f"{value} != {dict2[key]}"
                    ])
                    raise ValueError(output_error)
                return False
    return True


class TestLoadConfig(unittest.TestCase):
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
        template_file = 'parent_template.yml'
        config_file = 'child_template.yml'
        with open(template_file, 'w', encoding='utf-8') as file:
            file.write(
                'key0: value1\nkey1: value2\nkey2: value3\nkey3: value4\nkey4: value5\n')

        with open(config_file, 'w', encoding='utf-8') as file:
            file.write(
                'templates:\n  - parent_template.yml\nkey2: value1\nkey3: value2\n')

        expected_config = {
            'key0': 'value1',
            'key1': 'value2',
            'key2': 'value1',
            'key3': 'value2',
            'key4': 'value5'
        }
        actual_config = load_config(config_file)
        # Clean up
        os.remove(config_file)
        os.remove(template_file)
        self.assertEqual(actual_config, expected_config)

    def test_load_config_invalid_template(self):
        config_file = 'invalid_template.yaml'
        with open(config_file, 'w', encoding='utf-8') as file:
            file.write(
                'templates:\n  - fake_template.yml\nkey0: value1\nkey1: value2\n2: value3\n')

        with self.assertRaises(Exception):
            load_config(config_file)
        # Clean up
        os.remove(config_file)

    def test_load_config_with_template_args(self):
        template_file = 'template_with_args.yml'
        config_file = 'config_with_args.yml'
        with open(template_file, 'w', encoding='utf-8') as file:
            file.write('key0: value1\nkey1: !key2\n')

        with open(config_file, 'w', encoding='utf-8') as file:
            content = "".join([
                'templates:\n'
                f'  - path: {template_file}\n',
                '    inputs:\n',
                '      key2: value2\n'
            ])
            file.write(content)

        expected_config = {
            'key0': 'value1',
            'key1': 'value2'
        }
        actual_config = load_config(config_file)
        # Clean up
        os.remove(config_file)
        os.remove(template_file)
        self.assertEqual(actual_config, expected_config)

    def test_load_config_with_repeated_template_args(self):
        template_file = 'template_with_args.yml'
        config_file = 'config_with_args.yml'
        with open(template_file, 'w', encoding='utf-8') as file:
            file.write('section:\n  - key1: !key2\n')

        with open(config_file, 'w', encoding='utf-8') as file:
            content = "".join([
                'templates:\n'
                f'  - path: {template_file}\n',
                '    inputs:\n',
                '      key2: value2\n',
                f'  - path: {template_file}\n',
                '    inputs:\n',
                '      key2: value3\n'
            ])
            file.write(content)

        expected_config = {
            'section': [
                {'key1': 'value2'},
                {'key1': 'value3'}
            ]
        }
        actual_config = load_config(config_file)
        # Clean up
        os.remove(config_file)
        os.remove(template_file)
        self.assertEqual(actual_config, expected_config)

    def test_load_config_with_template_overwrite(self):
        template_file0 = 'template0.yml'
        template_file1 = 'template1.yml'
        config_file = 'config_with_template_override.yml'
        with open(template_file0, 'w', encoding='utf-8') as file:
            content = "".join([
                'key0: value1\n',
                'key1: value2\n',
                'key2:\n',
                '  - subkey0: subvalue0\n',
                '    subkey1: subvalue1\n'
            ])
            file.write(content)

        with open(template_file1, 'w', encoding='utf-8') as file:
            content = "".join([
                'key1: value3\n',
                'key2:\n',
                '  - subkey0: subvalue4\n',
            ])
            file.write(content)

        with open(config_file, 'w', encoding='utf-8') as file:
            content = "".join([
                'templates:\n'
                f'  - {template_file0}\n',
                f'  - path: {template_file1}\n',
                 '    overwrite: true\n'
                 'key2:\n',
                 '  - subkey0: "subvalue2"\n',
                 '    subkey1: "subvalue3"\n\n'
            ])
            file.write(content)

        expected_config = {
            'key0': 'value1',
            'key1': 'value3',
            'key2': [
                {'subkey0': 'subvalue4'},
                {'subkey0': 'subvalue2', 'subkey1': 'subvalue3'}
            ]
        }
        actual_config = load_config(config_file)
        # Clean up
        os.remove(config_file)
        os.remove(template_file0)
        os.remove(template_file1)
        self.assertTrue(compare_dicts(actual_config, expected_config))

    def test_load_config_with_template_overwrite_false(self):
        template_file0 = 'template0.yml'
        template_file1 = 'template1.yml'
        config_file = 'config_with_template_override.yml'
        with open(template_file0, 'w', encoding='utf-8') as file:
            content = "".join([
                'key0: value1\n',
                'key1: value2\n',
                'key2:\n',
                '  - subkey0: subvalue0\n',
                '    subkey1: subvalue1\n'
            ])
            file.write(content)

        with open(template_file1, 'w', encoding='utf-8') as file:
            content = "".join([
                'key1: value3\n',
                'key2:\n',
                '  - subkey0: subvalue4\n',
            ])
            file.write(content)

        with open(config_file, 'w', encoding='utf-8') as file:
            content = "".join([
                'templates:\n'
                f'  - {template_file0}\n',
                f'  - path: {template_file1}\n',
                 '    overwrite: false\n'
                 'key2:\n',
                 '  - subkey0: "subvalue2"\n',
                 '    subkey1: "subvalue3"\n\n'
            ])
            file.write(content)

        expected_config = {
            'key0': 'value1',
            'key1': 'value3',
            'key2': [
                {'subkey0': 'subvalue0', 'subkey1': 'subvalue1'},
                {'subkey0': 'subvalue2', 'subkey1': 'subvalue3'},
                {'subkey0': 'subvalue4'}
            ]
        }
        actual_config = load_config(config_file)
        # Clean up
        os.remove(config_file)
        os.remove(template_file0)
        os.remove(template_file1)
        self.assertTrue(compare_dicts(actual_config, expected_config))


class TestRenderTemplate(unittest.TestCase):
    def test_render_template_no_args(self):
        src_template = "".join([
            'key0: value1\n',
            'key1: value2\n',
            'key2: value3\n',
        ])
        expected_rendered = "".join([
            'key0: value1\n',
            'key1: value2\n',
            'key2: value3\n',
        ])
        actual_rendered = render_template(src_template)
        self.assertEqual(actual_rendered, expected_rendered)

    def test_render_template_with_args(self):
        src_template = "".join([
            'key0: value1\n',
            'key1: value2\n',
            'key2: !key3\n',
        ])
        input_args = {'key3': 'value3'}
        expected_rendered = "".join([
            'key0: value1\n',
            'key1: value2\n',
            'key2: value3\n',
        ])
        actual_rendered = render_template(src_template, input_args)
        self.assertEqual(actual_rendered, expected_rendered)


class TestDeepMergeDicts(unittest.TestCase):
    def test_deep_merge_dicts_no_conflicts(self):
        source = {
            'key0': 'value1',
            'key1': 'value2',
            'key2': 'value3'
        }
        destination = {
            'key3': 'value4',
            'key4': 'value5',
            'key5': 'value6'
        }
        expected_merged = {
            'key0': 'value1',
            'key1': 'value2',
            'key2': 'value3',
            'key3': 'value4',
            'key4': 'value5',
            'key5': 'value6'
        }
        actual_merged = deep_merge_dicts(source, destination)
        self.assertTrue(compare_dicts(actual_merged, expected_merged))

    def test_deep_merge_dicts_with_conflicts(self):
        source = {
            'key0': 'value1',
            'key1': 'value2',
            'key2': 'value3'
        }
        destination = {
            'key1': 'value4',
            'key2': 'value5',
            'key3': 'value6'
        }
        expected_merged = {
            'key0': 'value1',
            'key1': 'value2',
            'key2': 'value3',
            'key3': 'value6'
        }
        actual_merged = deep_merge_dicts(source, destination)
        self.assertTrue(compare_dicts(actual_merged, expected_merged))

    def test_deep_merge_dicts_with_nested_dicts(self):
        source = {
            'key0': 'value1',
            'key1': {
                'subkey0': 'subvalue'
            }
        }
        destination = {
            'key1': {
                'subkey1': 'subvalue2'
            },
            'key2': 'value3'
        }
        expected_merged = {
            'key0': 'value1',
            'key1': {
                'subkey0': 'subvalue',
                'subkey1': 'subvalue2'
            },
            'key2': 'value3'
        }
        actual_merged = deep_merge_dicts(source, destination)
        self.assertTrue(compare_dicts(actual_merged, expected_merged))

    def test_deep_merge_dicts_with_dict_list(self):
        source = {
            'key0': 'value1',
            'key1': [
                {'subkey0': 'subvalue1'},
                {'subkey1': 'subvalue2'}
            ]
        }
        destination = {
            'key1': [
                {'subkey1': 'subvalue3'},
                {'subkey2': 'subvalue4'}
            ],
            'key2': 'value3'
        }
        expected_merged = {
            'key0': 'value1',
            'key1': [
                {'subkey0': 'subvalue1'},
                {'subkey1': 'subvalue2'},
                {'subkey1': 'subvalue3'},
                {'subkey2': 'subvalue4'}
            ],
            'key2': 'value3'
        }
        actual_merged = deep_merge_dicts(source, destination)
        self.assertTrue(compare_dicts(actual_merged, expected_merged))

    def test_deep_merge_dicts_with_list(self):
        source = {
            'key0': 'value1',
            'key1': ['subvalue1', 'subvalue2'],
            'key2': 'value2'
        }
        destination = {
            'key1': ['subvalue3', 'subvalue4'],
            'key2': 'value3'
        }
        expected_merged = {
            'key0': 'value1',
            'key1': ['subvalue1', 'subvalue2', 'subvalue3', 'subvalue4'],
            'key2': 'value2'
        }
        actual_merged = deep_merge_dicts(source, destination)
        self.assertTrue(compare_dicts(actual_merged, expected_merged))

    def test_deep_merge_dicts_with_incompatible_types(self):
        source = {
            'key0': 'value1',
            'key1': 'value2'
        }
        destination = {
            'key1': ['subvalue1', 'subvalue2'],
            'key2': 'value3'
        }

        with self.assertRaises(TypeError):
            deep_merge_dicts(source, destination)

    def test_deep_merge_dicts_with_overwrite(self):
        source = {
            'key0': 'value1',
            'key1': ['subvalue1', 'subvalue2'],
        }
        destination = {
            'key1': 'value3',
            'key2': 'value4'
        }
        expected_merged = {
            'key0': 'value1',
            'key1': ['subvalue1', 'subvalue2'],
            'key2': 'value4'
        }

        actual_merged = deep_merge_dicts(source, destination, overwrite=True)
        self.assertTrue(compare_dicts(actual_merged, expected_merged))


class TestValidateTemplate(unittest.TestCase):
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
