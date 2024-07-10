"""
This module is used to validate various aspects of the templates and the
config file, such as the keys in a dictionary, and the structure of the
config file. Some validation is done by checking against the provided schema,
and by checking for required fields.
"""
import os

SUPPORTED_TYPES = (str, int, float, bool, dict, list)

def get_python_type(value: str) -> type:
    # pylint: disable=too-many-return-statements
    """
    Get the Python type of a string value.
    
    Args:
        value (str): The string value to get the Python type of.
    
    Returns:
        type: The Python type of the value.
    """
    if value is None:
        return None
    if value.lower() in ['str', 'string']:
        return str
    if value.lower() in ['int', 'integer']:
        return int
    if value.lower() in ['float', 'double']:
        return float
    if value.lower() in ['bool', 'boolean']:
        return bool
    if value.lower() in ['dict', 'dictionary', 'object', 'map']:
        return dict
    if value.lower() in  ['list', 'array', 'sequence', 'tuple', 'collection']:
        return list
    raise ValueError("Invalid type")

def search_input_file(input_file: str, kind='schema', directories=None) -> str:
    """
    Search for an input file in several locations.
    The precedence is as follows:
    1. The specified input file path/name, if it exists (absolute or relative).
    2. The directories specified in the YAMELINNO_<kind> environment variable. I.e.
         YAMELINNO_SCHEMAS for schemas, YAMELINNO_TEMPLATES for templates, etc.
    3. The directories specified in the directories argument. This is useful for
         specifying directories in the command line or to make sure the search
         includes the directory where another file which sourced this input file
         is located.

    Args:
        input_file (str): The path to the input file.
        kind (str): The kind of file being searched for. Default is 'schema'.
        directories (list): A list of directories to search in. Default is None.

    Returns:
        str: The path to the input file.

    Raises:
        FileNotFoundError: If the input file is not found.
    """
    searched_locations = []
    env_var = f"YAMELINNO_{kind.upper() + 'S'}"
    if os.path.exists(input_file):
        return input_file
    searched_locations.append(input_file)
    # If the YAMELINNO_<kind> environment variable is set,
    # verify if its a list of directories separated by a colon
    if env_var in os.environ:
        env_directories = \
            [os.environ[env_var]] if ":" not in os.environ[env_var] \
            else os.environ[env_var].strip().strip(':').split(':')
        # Check if the directories are valid
        for directory in env_directories:
            if not os.path.isdir(directory):
                raise FileNotFoundError(
                    f"Directory {directory} not found. env_var: {env_var}")
            input_file_path = os.path.join(directory, input_file)
            if os.path.exists(input_file_path):
                return input_file_path
            searched_locations.append(input_file_path)
    # If the directories argument is provided, search in them
    if directories is None:
        directories = []
    for directory in directories:
        input_file_path = os.path.join(directory, input_file)
        if os.path.isdir(directory) and os.path.exists(input_file_path):
            return input_file_path
        searched_locations.append(input_file_path)
    raise FileNotFoundError(
        f"Input {kind} {input_file} not found. Searched in: {searched_locations}")


def validate_dict_keys(dict_value) -> None:
    """
    Validate a dictionary provided as a value in a template
    to ensure it has only keys that are strings.
    
    Args:
        dict_value (dict): The dictionary to validate.

    Raises:
        TypeError: If a key is not a string.
    """
    for key, value in dict_value.items():
        if not isinstance(key, str):
            raise TypeError("Keys in dictionary must be strings")
        if isinstance(value, dict):
            validate_dict_keys(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    validate_dict_keys(item)
        elif not isinstance(value, SUPPORTED_TYPES):
            raise TypeError(
                f"Values in dictionary must be one of the supported types:{SUPPORTED_TYPES}"
            )


def get_required_sections(schema) -> list:
    """
    Get a list of required sections from the schema.
    
    Args:
        schema (dict): The schema to get the required sections from.
    
    Returns:
        list: A list of required sections.
    """
    required_sections = []
    for key, value in schema.items():
        if value.get('required', False):
            required_sections.append(key)
    return required_sections


def get_key_types(key_definition) -> list:
    """
    Get the types of keys from a key or entry definition.
    
    Args:
        key_definition (dict): The definition of the keys.
    
    Returns:
        list: A list of tuples in the form (key, type, required).
    """
    key_types = []
    for key, value in key_definition.items():
        if 'type' not in value:
            key_type = None
        else:
            key_type = get_python_type(value['type'])
        key_types.append((key, key_type, value.get('required', False)))
    return key_types


def validate_key_types(key_types, keys_dict) -> None:
    """
    Validate the types of keys in a section or entry.
    
    Args:
        key_types (list): A list of tuples in the form (key, type, required).
        keys_dict (dict): The section or entry to validate.
    
    Raises:
        TypeError: If a key is of the wrong type.
    """
    for key, key_type, required in key_types:
        if key not in keys_dict:
            if required:
                output_error = "".join([
                    f"Required key '{key}' missing.\n",
                    f"keys_dict: {keys_dict}\n",
                    f"key_types: {key_types}"
                ])
                raise KeyError(output_error)
        if key_type is None:
            # No type specified, so we can't validate
            continue
        if not isinstance(keys_dict[key], key_type):
            raise TypeError(f"Key '{key}' must be of type {key_type}")
    # Now check the other way around
    for key in keys_dict:
        if key not in [k for k, _, _ in key_types]:
            raise KeyError(f"Key '{key}' not found in schema")


def validate_keys(keys_dict, section_definition, entry=False) -> None:
    """
    Validate the keys of a section or entry against its definition.
    
    Args:
        section (dict): The section to validate.
        section_definition (dict): The definition of the section.
        entry (bool): Whether the section is an entry or not.

    Raises:
        KeyError: If a required key is missing.
        KeyError: If a required key is missing.
        TypeError: If a key is of the wrong type.
    """
    section_def = section_definition['keys'] if not entry else section_definition['entry']
    key_types = get_key_types(section_def)
    validate_key_types(key_types, keys_dict)


def validate_section(section, section_definition) -> None:
    """
    Validate a section against its definition.
    
    Args:
        section (dict): The section to validate.
        section_definition (dict): The definition of the section.
    
    Raises:
        KeyError: If the section has incompatible children type.
        KeyError: If a required key is missing.
        KeyError: If a required entry key is missing.
    """
    if section_definition['children'] == 'keys':
        # Validate required keys
        validate_keys(section, section_definition)

    elif section_definition['children'] == 'entries':
        # Validate required entry keys
        for entry in section:
            validate_keys(entry, section_definition, entry=True)

    elif section_definition['children'] == 'raw':
        # Validate required raw field
        if section_definition.get('required', False):
            if 'raw' not in section:
                raise KeyError("Required raw field missing")
        if 'raw' in section:
            if not isinstance(section['raw'], str):
                raise TypeError("Raw field must be a string")

def validate_config(config, schema) -> None:
    """
    Validate a configuration against a schema.
    
    Args:
        config (dict): The configuration to validate.
        schema (dict): The schema to validate against.
    
    Raises:
        KeyError: If a required section is missing.
        KeyError: If a required key is missing.
        KeyError: If a required entry key is missing.
        TypeError: If a key is of the wrong type.
    """
    # Validate if the required sections are present
    required_sections = get_required_sections(schema)
    for section_name in required_sections:
        if section_name not in config:
            raise KeyError(f"Required section '{section_name}' missing")
    # Validate section content
    for section_name, section in config.items():
        validate_section(section, schema[section_name])
