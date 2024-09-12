#!/usr/bin/env python3
"""
This module contains the main function for rendering a configuration
using a schema and printing the rendered configuration.
"""
import os
import argparse

from src.templates import load_config
from src.rendering import render, load_schema
from src.validation import validate_config

def get_startup_configurations(argv=None) -> argparse.Namespace:
    """
    Retrieves the startup configurations from the command line arguments.

    Returns:
        argparse.Namespace: An object containing the parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog='yamelinno',
        description='Render a configuration using\
            a schema and print the rendered configuration.')
    parser.add_argument('input_file', help='Input YAML file')
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        default='stdout',
        help='Output file. If not specified, the output will be printed \
            to stdout.')
    parser.add_argument(
        '-s', '--schema',
        dest='schema_file',
        help='Schema file. If not specified, the schema will be read from \
            "schema.yml", which must be in the same directory as the input file.')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='yamelinno 0.1',
        help='Display the version of the tool.')
    args = parser.parse_args(argv)

    # Check if the input file exists
    if not os.path.exists(args.input_file):
        parser.error(f"Input file '{args.input_file}' not found")

    # Check if the schema file is specified
    if not args.schema_file:
        # If not specified, assume the base-schema file from this project
        args.schema_file = "base-schema.yml"

    return args


def main(argv=None) -> None:
    """
    Main function that loads the configuration and schema files,
    renders the configuration using the schema, and prints the
    rendered configuration.
    """
    args = get_startup_configurations(argv)
    config = load_config(args.input_file)
    schema = load_schema(args.schema_file)
    validate_config(config, schema)
    rendered_config = render(config, schema)

    if args.output_file == 'stdout':
        print(rendered_config)
    else:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(rendered_config)

if __name__ == '__main__':
    main()
