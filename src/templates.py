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
        overwrite (bool): Whether to overwrite values from templates, instead of
            merging them. Default is False.

    Returns:
        list: The loaded config as a dict.

    """
    with open(config_file, 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        # Parse the templates
        if 'templates' not in config:
            # This is a simple config file
            # with no templates
            return config
        # There are templates to parse
        merged_config = {}
        for t in config['templates']:
            # Compatibility with old templates
            if isinstance(t, str):
                t = {'path': t, 'inputs': {}}
            if 'path' not in t:
                raise KeyError("Template path not specified")
            template_args = t.get('inputs', {})
            overwrite_destination = t.get('overwrite', False)
            template = load_template(t['path'], template_args)
            merged_config = deep_merge_dicts(template, merged_config, overwrite_destination)
        config.pop('templates', None)
        merged_config = deep_merge_dicts(config, merged_config)
        return merged_config


def render_template(src_template, input_args=None) -> str:
    """
    Render a template with the provided input arguments.
    It works by replacing the placeholders in the template,
    such as !input_arg, with the values from the input arguments.
    It does so reading the template as raw text and using the
    Python string format method.

    Args:
        src_template (dict): The source template to render.
        input_args (dict): The input arguments to the template.
    
    Returns:
        str: The rendered template as a string.
    # TODO: Add support for !! escaping in the template
    """
    if input_args is not None:
        for key, value in input_args.items():
            if "!" + key in src_template:
                src_template = src_template.replace("!" + key, str(value))
            else:
                raise KeyError(f"Input argument {key} not found in template")
    return src_template


def load_template(template_file, input_args=None) -> dict:
    """
    Load a template file with or without children templates.
    If a template has children templates, they are loaded recursively.

    Args:
        template_file (str): The path to the template file.
        input_args (dict): The input arguments to the template
        overwrite_destination (bool): Whether to overwrite values in the destination,
            instead of merging them. Default is False.

    Returns:
        list: The loaded template as a dict.

    """
    with open(template_file, 'r', encoding='utf-8') as file:
        # Apply input arguments to the template
        src_template = file.read()
        template = yaml.load(render_template(src_template, input_args), Loader=yaml.FullLoader)
        # Validate the template
        validate_template(template)
        # Parse the template
        if 'templates' not in template:
            # This is a leaf template
            return template
        # This is a parent template
        merged_template = {}
        for t in template['templates']:
            # Compatibility with old templates
            if isinstance(t, str):
                t = {'path': t, 'inputs': {}}
            if 'path' not in t:
                raise KeyError("Template path not specified")
            template_args = t.get('inputs', {})
            overwrite_destination = t.get('overwrite', False)
            merged_template = deep_merge_dicts(
                load_template(t['path'], template_args), merged_template)
        template.pop('templates', None)
        merged_template = deep_merge_dicts(template, merged_template, overwrite_destination)
        return merged_template


def deep_merge_dicts(source: dict, destination: dict, overwrite: bool = False) -> dict:
    """
    Recursively merges source and destination dictionaries.

    Args:
        source (dict): The dictionary to merge from.
        destination (dict): The dictionary to merge into.
        overwrite (bool): Whether to overwrite values in the destination.

    Returns:
        dict: The merged dictionary.

    """
    if overwrite:
        destination.update(source)
        return destination

    for key, value in source.items():
        if isinstance(value, dict):
            # Get node or create one
            node = destination.setdefault(key, {})
            deep_merge_dicts(value, node)
        elif isinstance(value, list):
            # Get node or create one
            node = destination.setdefault(key, [])
            for item in value:
                node.append(item)
        else:
            if key in destination:
                if not isinstance(destination[key], type(value)):
                    raise TypeError(f"Type mismatch for key {key}")
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