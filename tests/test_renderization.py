import unittest

from src.renderization import render, render_entry, render_section, render_key

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
        expected_output = 'KeyName: value; '
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
        expected_output = '[SectionName]\nKeyName=value\n\n'
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
        expected_output = '[SectionName]\nKeyName=value\nKeyName2=value2\n\n'
        rendered_section = render_section(section, section_definition)
        self.assertEqual(rendered_section, expected_output)
    

    def test_render_section_with_entries(self):
        section = [
            {
                'keyName': 'value1'
            },
            {
                'keyName': 'value2'
            }
        ]
        section_definition = {
            'renderedName': 'SectionName',
            'children': 'entries',
            'entry': {
                'keyName': {
                    'renderedName': 'KeyName',
                    'required': True
                }
            }
        }
        expected_output = '[SectionName]\nKeyName: value1; KeyName: value2; \n'
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
            'rendered_name': 'SectionName',
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
        expected_output = '[SectionName]\nKeyName=value\n\n'
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
        expected_output = '[SectionName]\nKeyName: value1; KeyName: value2; \n'
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