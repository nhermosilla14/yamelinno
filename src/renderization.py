"""
This module is used to render the config file, from yaml to the
iss format. The iss format is expressed in yaml using the following
schema:     

```
sectionName:
    rendered_name: "SectionName"
    children: "keys" | "entries"
    # If children is "keys", the section is a list of key-value pairs
    keys:
        keyName:
            rendered_name: "KeyName"
            required: true | false
    # If children is "entries", the section is a list of entries, each
    # one a list of key-value pairs itself
    entry:
        keyName:
            rendered_name: "KeyName"
            required: true | false
```

This is rendered to the following format:

```
[SectionName]
# If children is "keys"
KeyName: value;

[AnyOtherSection]
# If children is "entries"
KeyName: value; KeyName2: value2;
```

"""

import yaml

def load_schema(schema_file) -> dict:
    """
    Load the schema file.

    Args:
        schema_file (str): The path to the schema file.

    Returns:
        dict: The loaded schema as a dictionary.

    Raises:
        FileNotFoundError: If the schema file does not exist.
        yaml.YAMLError: If there is an error parsing the schema file.
    """
    with open(schema_file, 'r', encoding='utf-8') as file:
        schema = yaml.load(file, Loader=yaml.FullLoader)
        return schema


def render_key(key, value, section_definition) -> str:
    """
    Renders a key-value pair based on the given section definition.

    Args:
        key (str): The key to render.
        value (str): The value associated with the key.
        section_definition (dict): The definition of the section containing the key.

    Returns:
        str: The rendered key-value pair in the format <rendered_name>=<value>.

    Raises:
        Exception: If the key is not found in the section definition.
    """

    if key not in section_definition['keys']:
        raise KeyError(f"Key '{key}' not found in section definition")

    key_definition = section_definition['keys'][key]

    # Render the key
    # Every key has a 'renderedName' field, which must be used as:
    # <renderedName>=<value>
    rendered_name = key_definition['renderedName']
    return f"{rendered_name}={value}"

def render_entry(entry, section_definition) -> str:
    """
    Renders an entry based on the given entry and section definition.

    Args:
        entry (dict): The entry to be rendered. It should be a dictionary.
        section_definition (dict): The section definition containing the 
        required keys and their properties.

    Returns:
        str: The rendered entry as a string.

    Raises:
        KeyError: If a key in the entry is not found in the section definition.
        KeyError: If a required key is missing in the entry.
    """
    # An entry is a dictionary. We need to verify that all keys in the entry
    # are present in the section_definition
    for key, value in entry.items():
        if key not in section_definition['entry']:
            raise KeyError(f"Key '{key}' not found in entry definition")
        # Now that we know that all keys are present in the section_definition
        # we need to check if every required key is present in the entry
        required_keys = [
            k for k, v in section_definition['entry'].items()
            if v.get('required', False)
        ]
        for required_key in required_keys:
            if required_key not in entry:
                raise KeyError(f"Required key '{required_key}' not found in entry")
        rendered_entry = ""
        for key, value in entry.items():
            rendered_name = section_definition['entry'][key]['renderedName']
            if isinstance(value, list):
                # If the value is a list, we need to render it as space-separated values
                rendered_entry += f"{rendered_name}:"
                for v in value:
                    rendered_entry += f" {v}"
            else:
                rendered_entry += f"{rendered_name}: {value}"
            rendered_entry += "; "
        rendered_entry = rendered_entry[:-2]  # Remove the last space and semicolon
        return rendered_entry


def render_raw(raw_str, section_definition) -> str:
    """
    Render the raw field of a section.

    Args:
        raw_str (str): The raw string to be rendered.
        section_definition (dict): The definition of the section.

    Returns:
        str: The rendered raw string.

    Raises:
        KeyError: If the section has incompatible children type.
    """
    # Check if the section has a raw field
    if section_definition['children'] != 'raw':
        raise KeyError("Incompatible children type found.")
    # Render the raw field
    return raw_str


def render_section(section, section_definition) -> str:
    """
    Renders a section based on its definition.

    Args:
        section (dict): The section to be rendered.
        section_definition (dict): The definition of the section.

    Returns:
        str: The rendered section as a string.
    """
    # A section can be a list of key-value pairs or a list of entries
    # We need to check the type of the section
    if 'children' not in section_definition:
        raise KeyError(f"No children definition found for section {section['name']}")

    rendered_section: str = ""
    # Get the rendered name of the section
    rendered_section += f"[{section_definition['renderedName']}]\n"
    # Check if the section has keys, entries or raw field
    if section_definition['children'] == 'keys':
        # Render the keys
        for key, value in section.items():
            rendered_section += render_key(key, value, section_definition)
            rendered_section += "\n"
    elif section_definition['children'] == 'entries':
        # Render the entries
        for entry in section:
            rendered_section += render_entry(entry, section_definition)
            rendered_section += "\n"
    elif section_definition['children'] == 'raw':
        # Render the raw field
        raw_str = section.get('raw', '')
        rendered_section += render_raw(raw_str, section_definition)
    rendered_section += "\n"
    return rendered_section


def render(config, schema) -> str:
    """
    Render the config file using the provided schema.

    Args:
        config (dict): The configuration dictionary.
        schema (dict): The schema dictionary.

    Returns:
        str: The rendered config file.
    """
    rendered_config = ""
    for section_name, section in config.items():
        section_definition = schema[section_name]
        rendered_section = render_section(section, section_definition)
        rendered_config += rendered_section
    return rendered_config
