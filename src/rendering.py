"""
This module is used to render the config file, from yaml to the
iss format. The iss format is expressed in yaml.
"""
import yaml

from src.validation import search_input_file

def search_schema(schema_file) -> str:
    """
    Search for a schema file in the current directory or in the directories
    specified by the YAMELINNO_SCHEMAS environment variable.

    Args:
        schema_file (str): The path to the schema file.

    Returns:
        str: The path to the schema file.

    Raises:
        FileNotFoundError: If the schema file is not found.
    """
    return search_input_file(input_file=schema_file, kind='schema')

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
    schema_file = search_schema(schema_file)
    with open(schema_file, 'r', encoding='utf-8') as file:
        schema = yaml.load(file, Loader=yaml.FullLoader)
        return schema


def render_value(value, target_type=None) -> str:
    """
    Render a value to a string following the iss format.
    For example: 
    - A list of values should be rendered as space-separated values.
    - A string should be rendered as is (with quotes, for extra safety).
    - A number should be rendered as a string (without quotes).
    - A boolean should be rendered as "yes" or "no" (without quotes)
    - A double-quote should be rendered as two double-quotes.

    Args:
        value: The value to be rendered.
        target_type: The target type of the value. If provided, the value
        will be converted to this type before rendering. This is currently
        not used, but is provided in order to support more complex types
        in the future, such as UUID, dates, URLs, etc.

    Returns:
        str: The rendered value as a string.
    """
    if target_type:
        print(f"Target type specifying is not supported yet. Value: {value}")
    if isinstance(value, list):
        # If the value is a list, render it as space-separated values
        return " ".join(value)
    if isinstance(value, str):
        # If the value is a string, render it with quotes
        # and escape any double-quotes
        return '"' + value.replace("\"", "\"\"") + '"'
    if isinstance(value, bool):
        # If the value is a boolean, render it as "yes" or "no"
        return "yes" if value else "no"

    # If the value is anything else, render it as a string
    return str(value)


def render_key(key, value, section_definition) -> str:
    """
    Renders a key-value pair based on the given section definition.

    Args:
        key (str): The key to render.
        value (str): The value associated with the key.
        section_definition (dict): The definition of the section containing the key.

    Returns:
        str: The rendered key-value pair in the format <rendered_name>=<value>.
    """
    key_definition = section_definition['keys'][key]

    # Render the key
    # Every key has a 'renderedName' field, which must be used as:
    # <renderedName>=<value>\
    rendered_name = key_definition['renderedName']
    return f"{rendered_name}={render_value(value)}"


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
            rendered_entry += f"{rendered_name}: {render_value(value)}"
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
