# pylint: disable=missing-docstring
import unittest

from src.validation import (
    get_python_type,
    get_key_types,
    validate_dict_keys,
    get_required_sections,
    validate_key_types,
    validate_keys,
    validate_section,
    validate_config
)

class TestValidationGetPythonType(unittest.TestCase):
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

    def test_get_python_type_invalid(self):
        with self.assertRaises(ValueError):
            get_python_type('invalid')

class TestValidationValidateDictKeys(unittest.TestCase):
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

class TestValidationGetRequiredSections(unittest.TestCase):
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


class TestValidationGetKeyTypes(unittest.TestCase):
    def test_get_key_types_complete(self):
        key_definitions = {
            'key0': {'type': 'str', 'required': True},
            'key1': {'type': 'int', 'required': False},
            'key2': {'type': 'bool'}
        }

        expected_key_types = [
            ('key0', str, True),
            ('key1', int, False),
            ('key2', bool, False)
        ]
        actual_key_types = get_key_types(key_definitions)
        self.assertEqual(actual_key_types, expected_key_types)

    def test_get_key_types_missing_type(self):
        key_definitions = {
            'key0': {'required': True},
            'key1': {'required': False}
        }
        expected_key_types = [
            ('key0', None, True),
            ('key1', None, False)
        ]
        actual_key_types = get_key_types(key_definitions)
        self.assertEqual(actual_key_types, expected_key_types)


class TestValidationValidateKeyTypes(unittest.TestCase):
    def test_validate_key_types_valid(self):
        key_types = [
            ('key0', str, True),
            ('key1', int, True),
            ('key2', bool, True),
            ('key3', float, True),
        ]
        keys_dict = {
            'key0': 'value0',
            'key1': 1,
            'key2': True,
            'key3': 3.14,
        }
        validate_key_types(key_types, keys_dict)

    def test_validate_key_types_with_none(self):
        required_keys = [
            ('key0', str, True),
            ('key1', int, True),
            ('key2', bool, True),
            ('key3', None, True),
        ]
        section = {
            'key0': 'value0',
            'key1': 1,
            'key2': True,
            'key3': 3.14,
        }
        validate_key_types(required_keys, section)

    def test_validate_key_types_invalid(self):
        key_types = [
            ('key0', str, True),
            ('key1', int, True),
            ('key2', bool, True),
            ('key3', float, True),
        ]
        keys_dict = {
            'key0': 'value0',
            'key1': 1,
            'key2': 'True',
            'key3': 3.14,
        }
        with self.assertRaises(TypeError):
            validate_key_types(key_types, keys_dict)


    def test_validate_key_types_missing_key(self):
        key_types = [
            ('key0', str, True),
            ('key1', int, True),
            ('key2', bool, True),
            ('key3', float, True),
        ]
        keys_dict = {
            'key0': 'value0',
            'key1': 1,
            'key3': 3.14,
        }
        with self.assertRaises(KeyError):
            validate_key_types(key_types, keys_dict)

    def test_validate_key_types_extra_key(self):
        key_types = [
            ('key0', str, True),
            ('key1', int, True),
            ('key2', bool, True),
            ('key3', float, True),
        ]
        keys_dict = {
            'key0': 'value0',
            'key1': 1,
            'key2': True,
            'key3': 3.14,
            'key4': 'value4',
        }
        with self.assertRaises(KeyError):
            validate_key_types(key_types, keys_dict)


class TestValidationValidateKeys(unittest.TestCase):
    def test_validate_keys_valid_section(self):
        section = {
            'key0': 'value0',
            'key1': 1,
        }
        section_definition = {
            'children': 'keys',
            'keys': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
            }
        }
        # This should not raise an exception
        validate_keys(section, section_definition)

    def test_validate_keys_valid_entry(self):
        entry = {
            'key0': 'value0',
            'key1': 1,
        }
        section_definition = {
            'children': 'entries',
            'entry': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
            }
        }
        # This should not raise an exception
        validate_keys(entry, section_definition, entry=True)

    def test_validate_keys_invalid_section(self):
        section = {
            'key0': 'value0',
            'key1': '1',
        }
        section_definition = {
            'children': 'keys',
            'keys': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
            }
        }
        with self.assertRaises(TypeError):
            validate_keys(section, section_definition)

    def test_validate_keys_invalid_entry(self):
        entry = {
            'key0': 'value0',
            'key1': '1',
        }
        section_definition = {
            'children': 'entries',
            'entry': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
            }
        }
        with self.assertRaises(TypeError):
            validate_keys(entry, section_definition, entry=True)


class TestValidationValidateSection(unittest.TestCase):
    def test_validate_section_valid_keys_only(self):
        section = {
            'key0': 'value0',
            'key1': 1,
        }
        section_definition = {
            'children': 'keys',
            'keys': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
            }
        }
        # This should not raise an exception
        validate_section(section, section_definition)

    def test_validate_section_valid_entries_only(self):
        section = [
            {'key0': 'value0', 'key1': 1},
            {'key0': 'value2', 'key1': 2},
        ]
        section_definition = {
            'children': 'entries',
            'entry': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
            }
        }
        # This should not raise an exception
        validate_section(section, section_definition)

    def test_validate_section_valid_raw_only(self):
        section = {
            'raw': 'raw value'
        }
        section_definition = {
            'children': 'raw',
            'required': True
        }
        # This should not raise an exception
        validate_section(section, section_definition)

    def test_validate_section_invalid_keys_only(self):
        section = {
            'key0': 'value0',
            'key1': '1',
        }
        section_definition = {
            'children': 'keys',
            'keys': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
            }
        }
        with self.assertRaises(TypeError):
            validate_section(section, section_definition)

    def test_validate_section_invalid_entries_only(self):
        section = [
            {'key0': 'value0', 'key1': 1},
            {'key0': 'value2', 'key1': '2'},
        ]
        section_definition = {
            'children': 'entries',
            'entry': {
                'key0': {'type': 'str', 'required': True},
                'key1': {'type': 'int', 'required': True},
            }
        }

        with self.assertRaises(TypeError):
            validate_section(section, section_definition)

    def test_validate_section_invalid_raw_only(self):
        section = {
            'raw': 123
        }
        section_definition = {
            'children': 'raw',
            'required': True
        }
        with self.assertRaises(TypeError):
            validate_section(section, section_definition)


class TestValidationValidateConfig(unittest.TestCase):
    def test_validate_config(self):
        schema = {
            'section0': {
                'required': True,
                'children': 'keys',
                'keys': {
                    'key0': {'type': 'str', 'required': True},
                    'key1': {'type': 'int', 'required': True},
                }
            },
            'section1': {
                'required': False,
                'children': 'keys',
                'keys': {
                    'key2': {'type': 'bool'},
                    'key3': {'type': 'float'},
                }
            }
        }
        config = {
            'section0': {
                'key0': 'value0',
                'key1': 1,
            },
            'section1': {
                'key2': True,
                'key3': 3.14,
            }
        }
        # This should not raise an exception
        validate_config(config, schema)

    def test_validate_config_missing_non_required_section(self):
        schema = {
            'section0': {
                'required': True,
                'children': 'keys',
                'keys': {
                    'key0': {'type': 'str', 'required': True},
                    'key1': {'type': 'int', 'required': True},
                }
            },
            'section1': {
                'required': False,
                'children': 'keys',
                'keys': {
                    'key2': {'type': 'bool'},
                    'key3': {'type': 'float'},
                }
            }
        }
        config = {
            'section0': {
                'key0': 'value0',
                'key1': 1,
            }
        }
        validate_config(config, schema)

    def test_validate_config_missing_required_section(self):
        schema = {
            'section0': {
                'required': True,
                'children': 'keys',
                'keys': {
                    'key0': {'type': 'str', 'required': True},
                    'key1': {'type': 'int', 'required': True},
                }
            },
            'section1': {
                'required': False,
                'children': 'keys',
                'keys': {
                    'key2': {'type': 'bool'},
                    'key3': {'type': 'float'},
                }
            }
        }
        config = {
            'section1': {
                'key2': True,
                'key3': 3.14,
            }
        }
        with self.assertRaises(KeyError):
            validate_config(config, schema)

if __name__ == '__main__':
    unittest.main()
