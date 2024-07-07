# pylint: disable=missing-docstring
import unittest

from src.rendering import \
    render, render_entry, render_section, render_key, render_raw

class RenderKeyTestCase(unittest.TestCase):
    def test_render_key(self):
        key = 'keyName'
        value = 'value'
        section_definition = {
            'keys': {
                    'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                }
            }
        }
        expected_output = 'KeyName=value'
        rendered_key = render_key(key, value, section_definition)
        self.assertEqual(rendered_key, expected_output)

    def test_render_key_with_missing_required_key(self):
        key = 'anotherKeyName'
        value = 'value'
        key_definition = {
            'keyName': {
                'renderedName': 'KeyName',
                'required': True
            }
        }
        with self.assertRaises(Exception):
            render_key(key, value, key_definition)


class RenderEntryTestCase(unittest.TestCase):
    def test_render_entry(self):
        entry = {
            'keyName': 'value'
        }
        section_definition = {
            'entry': {
                'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                }
            }
        }
        expected_output = 'KeyName: value'
        rendered_entry = render_entry(entry, section_definition)
        self.assertEqual(rendered_entry, expected_output)

    def test_render_entry_with_list(self):
        entry = {
            'keyName': ['value1', 'value2']
        }
        section_definition = {
            'entry': {
                'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                }
            }
        }
        expected_output = 'KeyName: value1 value2'
        rendered_entry = render_entry(entry, section_definition)
        self.assertEqual(rendered_entry, expected_output)

    def test_render_entry_with_missing_required_key(self):
        entry = {
            'anotherKeyName': 'value'
        }
        section_definition = {
            'entry': {
                'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                },
                'anotherKeyName': {
                    'renderedName': 'AnotherKeyName',
                    'required': True
                }
            }
        }
        with self.assertRaises(Exception):
            render_entry(entry, section_definition)

class RenderRawTestCase(unittest.TestCase):
    def test_render_raw_return(self):
        raw_code = 'A single-line value'
        section_definition = {
            'renderedName': 'Code',
            'required': False,
            'children': 'raw',
        }
        expected_output = 'A single-line value'
        rendered_raw = render_raw(raw_code, section_definition)

        self.assertIsInstance(rendered_raw, str)
        self.assertEqual(rendered_raw, expected_output)

    def test_render_raw_multiline(self):
        section_definition = {
                'renderedName': 'Code',
                'required': False,
                'children': 'raw',
            }
        raw_code = "".join([
                'A multi-line\n',
                'value\n'
        ])
        expected_output = raw_code
        rendered_raw = render_raw(raw_code, section_definition)
        self.assertEqual(rendered_raw, expected_output)


class RenderSectionTestCase(unittest.TestCase):
    def test_render_section_with_single_key(self):
        section = {
            'keyName': 'value'
        }
        section_definition = {
            'renderedName': 'SectionName',
            'children': 'keys',
            'keys': {
                'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                }
            }
        }
        expected_output = "".join([
            '[SectionName]\n',
            'KeyName=value\n\n'
        ])
        rendered_section = render_section(section, section_definition)
        self.assertEqual(rendered_section, expected_output)


    def test_render_section_with_many_keys(self):
        section = {
            'keyName': 'value',
            'keyName2': 'value2'
        }
        section_definition = {
            'renderedName': 'SectionName',
            'children': 'keys',
            'keys': {
                'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                },
                'keyName2': {
                    'renderedName': 'KeyName2',
                    'required': True
                },
                'keyName3': {
                    'renderedName': 'KeyName3',
                    'required': False
                }
            }
        }
        expected_output = "".join([
            '[SectionName]\n',
            'KeyName=value\n',
            'KeyName2=value2\n\n'
        ])
        rendered_section = render_section(section, section_definition)
        self.assertEqual(rendered_section, expected_output)


    def test_render_section_with_entries(self):
        section = [
            {
                'keyName': 'value1'
            },
            {
                'keyName': 'value2',
                'anotherKeyName': 'value3'
            }
        ]
        section_definition = {
            'renderedName': 'SectionName',
            'children': 'entries',
            'entry': {
                'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                },
                'anotherKeyName': {
                    'renderedName': 'AnotherKeyName',
                    'required': False
                }
            }
        }
        expected_output = "".join([
            '[SectionName]\n',
            'KeyName: value1\n',
            'KeyName: value2; AnotherKeyName: value3\n\n'
        ])
        rendered_section = render_section(section, section_definition)
        self.assertEqual(rendered_section, expected_output)

    def test_render_section_with_missing_required_key(self):
        section = [
            {
                'keyName': 'value1'
            },
            {
                'anotherKeyName': 'value2'
            }
        ]
        section_definition = {
            'renderedName': 'SectionName',
            'children': 'entries',
            'entry': {
                'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                },
                'anotherKeyName': {
                    'renderedName': 'AnotherKeyName',
                    'required': True
                }
            }
        }
        with self.assertRaises(Exception):
            render_section(section, section_definition)


    def test_render_section_with_raw_code(self):
        # if yaml is not imported, do it
        if 'yaml' not in globals():
            import yaml #pylint: disable=import-outside-toplevel
        section_yml = "".join([
            "raw: |\n",
            "  function main() {\n",
            "      console.log(\"Hello World!\");\n",
            "  }"
        ])
        section = yaml.load(section_yml, Loader=yaml.FullLoader)
        self.assertIsInstance(section, dict)
        section_definition = {
            'renderedName': 'Code',
            'required': False,
            'children': 'raw',
        }

        expected_output = "".join([
            '[Code]\n',
            'function main() {\n',
            '    console.log("Hello World!");\n',
            '}\n'
        ])
        rendered_section = render_section(section, section_definition)
        self.assertEqual(rendered_section, expected_output)


class RenderTestCase(unittest.TestCase):
    def test_render_with_keys(self):
        config = {
            'sectionName': {
                'keyName': 'value'
            }
        }
        schema = {
            'sectionName': {
                'renderedName': 'SectionName',
                'children': 'keys',
                'keys': {
                    'keyName': {
                        'renderedName': 'KeyName',
                        'required': True
                    }
                }
            }
        }
        expected_output = [
            '[SectionName]\n'
            'KeyName=value\n\n'
        ]
        expected_output = "".join(expected_output)
        rendered_config = render(config, schema)
        self.assertEqual(rendered_config, expected_output)

    def test_render_with_entries(self):
        config = {
            'sectionName': [
                {
                    'keyName': 'value1'
                },
                {
                    'keyName': 'value2'
                }
            ]
        }
        schema = {
            'sectionName': {
                'renderedName': 'SectionName',
                'children': 'entries',
                'entry': {
                    'keyName': {
                        'renderedName': 'KeyName',
                        'required': True
                    }
                }
            }
        }
        expected_output = "".join([
            "[SectionName]\n"
            "KeyName: value1\n"
            "KeyName: value2\n\n"
        ])
        rendered_config = render(config, schema)
        self.assertEqual(rendered_config, expected_output)

    def test_render_with_missing_required_key(self):
        config = {
            'sectionName': [
                {
                    'keyName': 'value1'
                },
                {
                    'anotherKeyName': 'value2'
                }
            ]
        }
        schema = {
            'sectionName': {
                'renderedName': 'SectionName',
                'children': 'entries',
                'entry': {
                    'keyName': {
                        'renderedName': 'KeyName',
                        'required': True
                    },
                    'anotherKeyName': {
                        'renderedName': 'AnotherKeyName',
                        'required': True
                    }
                }
            }
        }
        with self.assertRaises(Exception):
            render(config, schema)

if __name__ == '__main__':
    unittest.main()
