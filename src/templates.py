"""
This module is used to merge the templates in order
to generate the initial yaml file. The templates are
merged in order, and the values from the last template
are used if there are conflicts.
"""

import yaml

def load_config(config_file) -> dict:
    """
    Load a config file with or without templates.
    If a template has children templates, they are loaded recursively.

    Args:
        config_file (str): The path to the config file.

    Returns:
        list: The loaded config as a dict.

    """
    with open(config_file, 'r', encoding='utf-8') as file:
        template = yaml.load(file, Loader=yaml.FullLoader)
        # Validate the template
        validate_template(template)
        # Parse the template
        if 'templates' not in template:
            # This is a leaf template
            return template
        else:
            # This is a parent template
            template_queue = []
            merged_config = {}
            for t in template['templates']:
                template_queue.append(load_config(t))
            for t in template_queue:
                merged_config = deep_merge_dicts(t, merged_config)
            template.pop('templates', None)
            merged_config = deep_merge_dicts(template, merged_config)
            return merged_config



def deep_merge_dicts(source, destination) -> dict:
    """
    Recursively merges source and destination dictionaries.

    Args:
        source (dict): The dictionary to merge from.
        destination (dict): The dictionary to merge into.

    Returns:
        dict: The merged dictionary.

    """
    for key, value in source.items():
        if isinstance(value, dict):
            # Get node or create one
            node = destination.setdefault(key, {})
            deep_merge_dicts(value, node)
        else:
            destination[key] = value
    return destination


def validate_template(template) -> None:
    """
    Check that a given template is valid, i.e., it has only valid keys and values.

    Args:
        template (dict): The template to validate.

    Raises:
        Exception: If the template is not a dictionary.
        Exception: If the 'templates' key is present but its value is not a list.
        Exception: If any key in the template is not a string.
        Exception: If any value in the template is not a string or a list.
    """
    supported_types = (str, list, dict, int, float, bool)
    if not isinstance(template, dict):
        raise TypeError("Template must be a dictionary")
    for key, value in template.items():
        if key == 'templates':
            if not isinstance(value, list):
                raise TypeError("Templates must be a list")
        elif not isinstance(key, str):
            raise KeyError(f"Invalid key type: {key}")
        elif not isinstance(value, supported_types):
            raise ValueError(f"Invalid value type: {value} for key {key}")
