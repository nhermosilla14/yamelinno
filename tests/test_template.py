# pylint: disable=missing-docstring
"""
Tests for the templates module.
"""

import unittest
import os

from src.templates import (
    search_template,
    load_config,
    render_template,
    deep_merge_dicts,
    validate_template,
)

def assert_equal_length(iter1, iter2) -> bool:
    """
    Compare the lengths of two dictionaries or 
    lists to check if they have the same number of items.

    Args:
        iter1 (dict): The first iterable to compare.
        iter2 (dict): The second iterable to compare.

    Returns:
        bool: True if the iterables have the same length, False otherwise.

    Raises:
        ValueError: If the iterables do not have the same number of items.
    """
    if len(iter1) == len(iter2):
        return True
    iter_type = "dictionaries" if isinstance(iter1, dict) else 'lists'
    if iter_type == 'lists':
        diff_msg = f"{iter1} != {iter2}"
    else:
        diff_msg = f"{iter1.keys()} != {iter2.keys()}"

    output_error = "".join([
            f"The {iter_type}",
            " do not have the same number of keys.\n",
            diff_msg
    ])
    raise ValueError(output_error)

def compare_lists(list1, list2) -> bool:
    """
    Compare two lists to check if they have the same items
    in any order.

    Args:
        list1 (list): The first list to compare.
        list2 (list): The second list to compare.

    Returns:
        bool: True if the lists have the same items, False otherwise.
    
    Raises:
        ValueError: If the lists do not have the same items
    """
    assert_equal_length(list1, list2)
    # The order of the items in the list does not matter
    if all(item in list2 for item in list1):
        return True
    output_error = "".join([
        "The lists do not have the same items.\n",
        f"{list1} != {list2}"
    ])
    raise ValueError(output_error)


def assert_equal_dicts(dict1, dict2) -> bool:
    """
    Compare two dictionaries to check if they have the same key-value pairs.

    Args:
        dict1 (dict): The first dictionary to compare.
        dict2 (dict): The second dictionary to compare.

    Returns:
        bool: True if the dictionaries have the same key-value pairs, False otherwise.
    
    Raises:
        ValueError: If the dictionaries do not have the same key-value pairs.

    """
    assert_equal_length(dict1, dict2)

    for key, value in dict1.items():
        if isinstance(value, dict):
            if not assert_equal_dicts(value, dict2[key]):
                output_error = "".join([
                    f"Value for key {key} does not match.\n",
                    f"{value} != {dict2[key]}"
                ])
                raise ValueError(output_error)

        elif isinstance(value, list):
            if len(value) != len(dict2[key]):
                output_error = "".join([
                    "The lists do not have the same number of items.\n",
                    f"{value} != {dict2[key]}"
                ])
                raise ValueError(output_error)

            # The order of the items in the list does not matter
            if not all(item in dict2[key] for item in value):
                output_error = "".join([
                    "The lists do not have the same items.\n",
                    f"{value} != {dict2[key]}"
                ])
                raise ValueError(output_error)
        else:
            if value != dict2[key]:
                output_error = "".join([
                    f"Value for key {key} does not match.\n",
                    f"{value} != {dict2[key]}"
                ])
                raise ValueError(output_error)
    return True

class TestAuxiliaryFunctions(unittest.TestCase):
    def test_assert_equal_length_true(self):
        dict1 = {'key0': 'value1', 'key1': 'value2'}
        dict2 = {'key0': 'value1', 'key1': 'value2'}

        self.assertTrue(assert_equal_length(dict1, dict2))

    def test_assert_equal_length_false(self):
        dict1 = {'key0': 'value1', 'key1': 'value2'}
        dict2 = {'key0': 'value1', 'key1': 'value2',
                    'key2': 'value3'}

        with self.assertRaises(ValueError):
            assert_equal_length(dict1, dict2)

    def test_compare_lists_true(self):
        list1 = ['item0', 'item1', 'item2']
        list2 = ['item2', 'item1', 'item0']

        self.assertTrue(compare_lists(list1, list2))

    def test_compare_lists_diff_items(self):
        list1 = ['item0', 'item1', 'item2']
        list2 = ['item2', 'item1', 'item3']

        with self.assertRaises(ValueError):
            compare_lists(list1, list2)

    def test_compare_lists_diff_length(self):
        list1 = ['item0', 'item1', 'item2']
        list2 = ['item2', 'item1']

        with self.assertRaises(ValueError):
            compare_lists(list1, list2)


    def test_assert_equal_dicts_true(self):
        dict1 = {'key0': 'value1', 'key1': 'value2'}
        dict2 = {'key1': 'value2', 'key0': 'value1'}

        self.assertTrue(assert_equal_dicts(dict1, dict2))

    def test_assert_equal_dicts_false(self):
        dict1 = {'key0': 'value1', 'key1': 'value2'}
        dict2 = {'key1': 'value2', 'key0': 'value3'}

        with self.assertRaises(ValueError):
            assert_equal_dicts(dict1, dict2)

class TestSearchTemplate(unittest.TestCase):
    def test_search_template_leaf_template(self):
        template_file = 'leaf_template.yaml'
        with open(template_file, 'w', encoding='utf-8') as file:
            file.write('key0: value1\nkey1: value2\nkey2: value3\n')

        expected_path = template_file
        actual_path = search_template(template_file)
        # Clean up
        os.remove(template_file)
        self.assertEqual(actual_path, expected_path)

    def test_search_template_same_dir_as_template(self):
        template_file = 'leaf_template.yaml'
        # Create a tmp directory
        os.mkdir('tmp')
        with open(f'tmp/{template_file}', 'w', encoding='utf-8') as file:
            file.write('key0: value1\nkey1: value2\nkey2: value3\n')

        expected_path = f'tmp/{template_file}'
        actual_path = search_template(template_file, ['tmp'])
        # Clean up
        os.remove(f'tmp/{template_file}')
        os.rmdir('tmp')
        self.assertEqual(actual_path, expected_path)

    def test_search_template_env_var(self):
        template_file = 'leaf_template.yaml'
        # Create a tmp directory
        os.mkdir('tmp')
        with open(f'tmp/{template_file}', 'w', encoding='utf-8') as file:
            file.write('key0: value1\nkey1: value2\nkey2: value3\n')

        os.environ['YAMELINNO_TEMPLATES'] = 'tmp'
        expected_path = f'tmp/{template_file}'
        actual_path = search_template(template_file)
        # Clean up
        os.remove(f'tmp/{template_file}')
        os.rmdir('tmp')
        self.assertEqual(actual_path, expected_path)


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

    def test_load_config_without_template_args(self):
        template_file = 'template_without_args.yml'
        config_file = 'config_without_args.yml'
        with open(template_file, 'w', encoding='utf-8') as file:
            file.write("".join([
                'key0: value1\n',
                'key1: value2\n'
                ])
            )

        with open(config_file, 'w', encoding='utf-8') as file:
            file.write(f'templates:\n  - {template_file}\n')

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
        self.assertTrue(assert_equal_dicts(actual_config, expected_config))

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
        self.assertTrue(assert_equal_dicts(actual_config, expected_config))


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

    def test_render_template_with_missing_args(self):
        src_template = "".join([
            'key0: value1\n',
            'key1: value2\n',
            'key2: !key3\n',
        ])
        input_args = {'key4': 'value4'}
        with self.assertRaises(KeyError):
            render_template(src_template, input_args)

    def test_render_template_without_its_args(self):
        src_template = "".join([
            'key0: value1\n',
            'key1: value2\n',
            'key2: !key3\n',
        ])
        expected_rendered = "".join([
            'key0: value1\n',
            'key1: value2\n',
            'key2: !key3\n',
        ])

        actual_rendered = render_template(src_template)
        self.assertEqual(actual_rendered, expected_rendered)

    def test_render_template_without_args_brief(self):
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
        actual_rendered = render_template(src_template, None)

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
        self.assertTrue(assert_equal_dicts(actual_merged, expected_merged))

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
        self.assertTrue(assert_equal_dicts(actual_merged, expected_merged))

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
        self.assertTrue(assert_equal_dicts(actual_merged, expected_merged))

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
        self.assertTrue(assert_equal_dicts(actual_merged, expected_merged))

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
        self.assertTrue(assert_equal_dicts(actual_merged, expected_merged))

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
        self.assertTrue(assert_equal_dicts(actual_merged, expected_merged))


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
