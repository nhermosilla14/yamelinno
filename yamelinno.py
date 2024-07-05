"""
This module contains the main function for rendering a configuration
using a schema and printing the rendered configuration.
"""

from src.templates import load_config
from src.renderization import render, load_schema

def main():
    """
    Main function that loads the configuration and schema files,
    renders the configuration using the schema, and prints the
    rendered configuration.
    """
    config = load_config('config.yml')
    schema = load_schema('schema.yml')
    rendered_config = render(config, schema)
    print(rendered_config)

if __name__ == '__main__':
    main()