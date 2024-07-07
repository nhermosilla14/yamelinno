"""
This module is used to validate various aspects of the templates and the
config file, such as the keys in a dictionary, and the structure of the
config file. Some validation is done by checking against the provided schema,
and by checking for required fields.
"""

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


def get_required_keys(section_definition, entry=False) -> list:
    """
    Get a list of required keys from a section definition or entry.
    Each key is retrieved along with its type, and returned as a tuple.
    
    Args:
        section_definition (dict): The section definition to get the required keys from.
        entry (bool): Whether the section is an entry or not.

    Returns:
        list: A list of required key-type tuples.
    """
    required_keys = []
    target_dict = section_definition['keys']\
        if not entry else section_definition['entry']
    for key, value in target_dict.items():
        if value.get('required', False):
            # Check if the key has a type defined
            key_type = get_python_type(value.get('type', None))
            required_keys.append((key, key_type))
    return required_keys


def validate_key_types(key_types, keys_dict, required=False) -> None:
    """
    Validate the types of keys in a section or entry.
    
    Args:
        key_types (list): A list of key-type tuples.
        keys_dict (dict): The section or entry to validate.
    
    Raises:
        TypeError: If a key is of the wrong type.
    """
    for key, key_type in key_types:
        if key not in keys_dict:
            if required:
                raise KeyError(f"Required key '{key}' missing")    
        if not isinstance(keys_dict[key], key_type):
            raise TypeError(f"Key '{key}' must be of type {key_type}")


def get_remaining_key_types(reference_key_schema, verified_keys) -> list:
    """
    Get a list of key-types tuples for the remaining keys in a section
    or entry.

    Args:
        reference_key_schema (dict): The schema of the keys.
        verified_keys (list): The keys that have already been verified.
    
    Returns:
        list: A list of key-type tuples for the remaining keys.
    """
    remaining_keys = set(reference_key_schema.keys()) - set(verified_keys)
    remaining_types = [
        get_python_type(reference_key_schema[key].get('type', None)
        ) for key in remaining_keys
    ]
    return list(zip(remaining_keys, remaining_types))


def validate_keys(section, section_definition, entry=False) -> None:
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
    # Validate required keys
    required_keys = get_required_keys(section_definition, entry=entry)
    validate_key_types(required_keys, section, required=True)
    # Validate other keys
    remaining_key_types = get_remaining_key_types(
        section_definition['keys'], [key for key, _ in required_keys])
    validate_key_types(remaining_key_types, section)


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
                raise KeyError(
                    f"Required raw field missing in section {section_definition['name']}"
                )
        if 'raw' in section:
            if not isinstance(section['raw'], str):
                raise TypeError(
                    f"Raw field must be a string in section {section_definition['name']}"
                )
