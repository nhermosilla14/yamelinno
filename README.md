# yamelinno
[![Pylint](https://github.com/nhermosilla14/yamelinno/actions/workflows/pylint.yml/badge.svg?branch=main)](https://github.com/nhermosilla14/yamelinno/actions/workflows/pylint.yml) 
[![Tests](https://github.com/nhermosilla14/yamelinno/actions/workflows/unittest.yml/badge.svg?branch=main)](https://github.com/nhermosilla14/yamelinno/actions/workflows/unittest.yml) 
![Coverage](https://nhermosilla14.github.io/yamelinno/badges.svg)
[![CodeQL](https://github.com/nhermosilla14/yamelinno/actions/workflows/github-code-scanning/codeql/badge.svg?branch=main)](https://github.com/nhermosilla14/yamelinno/actions/workflows/github-code-scanning/codeql)
[![Build and push container image](https://github.com/nhermosilla14/yamelinno/actions/workflows/container-publish.yml/badge.svg)](https://github.com/nhermosilla14/yamelinno/actions/workflows/container-publish.yml)
[![release badge](https://img.shields.io/github/v/release/nhermosilla14/yamelinno)](https://github.com/nhermosilla14/yamelinno/releases)
[![license badge](https://img.shields.io/github/license/nhermosilla14/yamelinno)](./LICENSE)

A tool to render yaml into InnoSetup iss files.

# Why?
I wanted to have a way to define my InnoSetup scripts in a more structured, reusable way, and I like yaml. I also happen to dislike a lot the InnoSetup scripting language, so I wanted to avoid it as much as possible. This tool is the result of that.

## Seriously, why?
Well, it's a fun project to work on, and I think it can be useful for some people. I also wanted to learn how to write a parser without using either Jinja or a super complex architecture, keeping it simple and easy to understand was in itself a challenge. 
Also, I wanted to achieve some things currently not possible with InnoSetup, like:

- Reusing code as templates or snippets.
- Defining the structure of the script in a more readable way.
- Having a schema to validate the input and provide hints to the user.
- Integrate with other tools that can generate yaml files, like a build system or a CI/CD pipeline.

# How?
The tool reads a yaml file and renders it into an InnoSetup iss file, which can then be compiled with the InnoSetup compiler.

# Features
- Render yaml into InnoSetup iss files.
- Maintain access to the InnoSetup constants and macros by using the `{}` syntax.
- Define templates to reuse code.
- Resolve templates recursively. A template can include other templates, which can include other templates, which can...
- Define a schema to validate the input yaml file. The schema is also a yaml file, so you can add missing keys and entries to the schema without having to modify the tool.
- Simple code base, easy to understand and modify. Tests have been written aiming at pretty much 100% coverage.

# Usage
```bash
yamelinno.py [options] <input_yml_file>

Options:
  -o, --output <output_file>  Output file. If not specified, the output will be printed to stdout.
  -s, --schema <schema_file>  Schema file. If not specified, the schema will be read from "base-schema.yml", which will be searched in any of the available schemas directories.
  -v, --version               Display the version of the tool.
  -h, --help                  Display this help message.
```

# Example
```yaml
# input.yml
setup:
  appId: '{2b6f0cc904d137be2e1730235f5664094b831186}' #UUID: 
  appName: "MyApp" #Name
  appVersion: "1.0" #Version

files:
  - source: "src/main.js"
    destDir: '{app}'
    flags:
      - ignoreversion
```

```yaml
# schema.yml
setup:
    renderedName: Setup
    children: keys
    required: true      
    keys:
      appId:
        renderedName: AppId
        required: true
      appName:
        renderedName: AppName
        required: true
      appVersion:
        renderedName: AppVersion
        required: true
      defaultDirName:
        renderedName: DefaultDirName
        required: false
      defaultDirPath:
        renderedName: DefaultDirPath
        required: false
  
files:
    renderedName: Files
    children: entries
    # Entry structure
    entry:
      source:
        renderedName: Source
        required: true
      destDir:
        renderedName: DestDir  
        required: true
      flags:
        renderedName: Flags
        required: false
```
With those files in place, you can run the tool like this:
```bash
yamelinno input.yml -o output.iss
```
and get:

```iss

[Setup]
AppId='{{2b6f0cc904d137be2e1730235f5664094b831186}'
AppName=MyApp
AppVersion=1.0

[Files]
Source: "src/main.js"; DestDir: "{app}"; Flags: ignoreversion

```

## Explanation
The tool reads the input file and searches recursively for the referenced templates. It then merges them into a single yaml file, validates it against the schema and, if the file is valid, proceeds to render the iss file. The schema is used to validate the input file and to provide hints to the user. More on that later.

# Templates
Templates are just pre-filled yaml files, which can be included in the main yaml file (or in other templates). They are resolved recursively, so a template can include other templates, which can include other templates, and so on. Here is an example:

```yaml
# template.yml
# A template to include a LICENSE file in the installation directory.
files:
  - source: "LICENSE"
    destDir: '{app}'
    flags:
      - ignoreversion
```

```yaml
# input.yml
setup:
  appId: '{2b6f0cc904d137be2e1730235f5664094b831186}' #UUID: 
  appName: "MyApp"
  appVersion: "1.0"

templates:
  - "template.yml"
```

```iss
[Setup]
AppId='{{2b6f0cc904d137be2e1730235f5664094b831186}'
AppName=MyApp
AppVersion=1.0

[Files]
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
```

The are two possible ways to include a template in the main yaml file:

1. By appending the path to a template to the list of `templates`. This is what is shown in the example above.
2. By using the extended syntax, which allows you to specify the path to the template file and the inputs to be used in the template. This is useful when you want to reuse a template with different values.

Here is an example of the extended syntax:
```yaml
# template.yml
# A template to include a file in the installation directory.
files:
  - source: '!sourceFile' # Single quotes are used to escape special characters.
    destDir: '{app}'
    flags:
      - ignoreversion
```
The `!sourceFile` key will be replaced by the value of the `sourceFile` key in the input file, as shown below.

```yaml
templates:
  - path: "template.yml" # Path to the template file.
    inputs: 
    # Values to be used in the template. To use special characters, such as `:`, or `#`,
    # you can surround the value with single quotes. Using '!' is unsupported yet.
      sourceFile: 'C:\LICENSE'
      # If overwrite is true, the values in the template will overwrite the values in the
      # previous templates. If false, the values in the template will be merged with the
      # values in the previous templates, trying to preserve as much information as possible.
      # That is, dictionaries will be merged (only conflicting keys will be overwritten), and
      # lists will be appended.
    overwrite: false
```
As a result, you will get:
```iss
[Files]
Source: "C:\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
```

Some more things to add:
- The `overwrite` key is optional, and defaults to `false`.
- The `inputs` key is optional, and defaults to an empty list.
- The `path` key is required if you are using the extended syntax.
- You can add the same template several times.
- The order in which the templates are included is important. The templates are resolved in the order they are included, so the last template will (most likely) overwrite the values in the previous templates.
- Templates are not validated against the schema, so you can include any yaml file as a template. This is useful when you want to include a snippet of code that is not part of the schema. The end result is validated against the schema, though.
- **IMPORTANT**: As the input values are resolved by simple string replacement, some issues may arise if the input values contain special characters or if an input value is fully contained in another input value. This is a known issue and will be addressed in future versions. A simple example of this is shown below:

```yaml
# template.yml
files:
  - source: '!sourceFile'
    destDir: '{app}\!source'
    flags:
      - ignoreversion
```
You would expect to use it as follows:
```yaml
templates:
  - path: "template.yml"
    inputs:
      source: 'myDir'
      sourceFile: 'C:\LICENSE'
```
But the result will be:
```iss
[Files]
Source: "myDirFile"; DestDir: "{app}\myDir"; Flags: ignoreversion
```
This is because the `sourceFile` value is fully contained in the `source` value, and in this case, the replacement is done in the order the values are resolved. This is a known issue and will be addressed in future versions. For now, you can avoid this by using different names for the input values.

## Path resolution
The path to the template file is resolved in the following way:
1. The path is checked as is. If the file exists, it is included, no matter if it's an absolute or relative path.
2. If the "YAMELINNO_TEMPLATES" environment variable is set, the path is checked against the directories in the variable. Many directories can be specified, separated by a colon. If the file exists in any of the directories, it is included. If an invalid directory is specified, it will raise an error.
3. If none of the above methods work, the tool will try to find the file in the same directory as file which referenced it in the `templates` key. This allows you to include templates that are in the same directory as the main yaml file, without having to specify the full path for any of them. You can also store all your templates in a single directory and reference them by filename only.
4. If none of the above methods work, the tool will raise an error.

# Schemas
The schema is a yaml file that defines the structure of the input yaml file. It is used to validate the input file and to provide hints to the user. The schema is also a yaml file, so you can modify it to add missing keys or entries without having to modify the tool. The attributes and structure of the schema are pretty much self-explanatory, but here is a brief explanation of the keys:

- `renderedName`: The name of the key in the rendered iss file.
- `children`: The type of the key. It can be `keys`, `entries` or `raw`. `keys` are used to define a dictionary, while `entries` are used to define a list of dictionaries (which follow the same schema that is defined in the `entry` key). `raw` is just a raw string that is rendered as is, useful for directives that don't follow the key-value structure (such as `[Code]`).
- `required`: Whether the key is required or not. If a key is required and not present in the input file, the tool will raise an error. This can be added to sections, keys, and entries.
- `keys`: A dictionary that defines the structure of the keys in the section. This is used to validate the input file and to provide hints to the user.
- `entry`: A dictionary that defines the structure of the entries in the section. This is used to validate the input file and to provide hints to the user.
- `type`: The type of the key. It can be `str`, `int`, `float`, `bool`, `list`, `dict`, among other variations. This is used to validate the input file. It's optional, so you can omit it if you don't want to validate the type of the key.

Here is an example of a schema file:

```yaml
setup:
    renderedName: Setup
    children: keys
    required: true      
    keys:
      appId:
        renderedName: AppId
        required: true
        type: str
      appName:
        renderedName: AppName
        required: true
      appVersion:
        renderedName: AppVersion
        required: true
      defaultDirName:
        renderedName: DefaultDirName
        required: false
      defaultDirPath:
        renderedName: DefaultDirPath
        required: false
```

A base schema is provided with the tool, so you can use it as a starting point to define your own schema. The base schema is pretty much the same as the schema above, but with more keys and entries defined. You can find it in the `schemas/base-schema.yml` file. If you want to use a different schema, you can specify it with the `-s` or `--schema` option. If you don't specify a schema, the tool will try to find the base schema in any of the available schemas directories.

NOTE: Although the provided schema does follow pretty much the same naming conventions as the InnoSetup directives, it doesn't have to be that way. You can define the keys and entries in the schema in any way you see fit, as long as you follow the structure defined above. As long as you keep the `renderedName` a valid InnoSetup directive, the tool will render it correctly.

## Schema resolution
Just like the templates, the schema is resolved in the following way:
1. The path is checked as is. If the file exists, it is included, no matter if it's an absolute or relative path.
2. If the "YAMELINNO_SCHEMAS" environment variable is set, the path is checked against the directories in the variable. Many directories can be specified, separated by a colon. If the file exists in any of the directories, it is included. If an invalid directory is specified, it will raise an error.
3. Schemas are not referenced in the input file so, if none of the above methods work, the tool will raise an error.

# Roadmap
- [X] Support for templates that can be resolved at runtime, either by the tool or by the user.
- [X] More InnoSetup directives in the base schema.
- [ ] Support for snippets, which are reusable code blocks that can be included in the yaml file.
- [ ] Add a wiki for better documentation, and to provide examples and tutorials.
- [ ] Add a repository with templates and schemas that can be used as a starting point.
- [ ] Support for brief syntax, which would allow the user to write the yaml file in a more concise way.
- [ ] Enable usage as a library, so it can be integrated with other tools.
- [ ] Port to Rust, because why not?

# Usage
You can use this tool in many ways, but here are some examples:
## As a script
You can run it directly as a python script. Just clone the repository, install the dependencies, and run the script with the desired options. For example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python yamelinno.py input.yml -o output.iss
```

You can also compile the script into an executable using `pyinstaller`. Just install `pyinstaller` and run the following command:

```bash
pyinstaller --onefile yamelinno.py
```

This will create an executable file in the `dist` directory. You can then run it as any other executable. This should work on Linux and Windows, but YMMV. 


## As a container
You can use the provided container image to run the tool. Just pull the image and run it with the desired options. For example:

```bash
podman run --rm -v $(pwd):/app ghcr.io/nhermosilla14/yamelinno:latest input.yml -o output.iss
```

## Building the container
You can build the container image yourself. Just clone the repository and build using the provided Containerfile. For example:

```bash
# Using podman is recommended
podman build -t yamelinno -f Containerfile .

# Or using docker
docker build -t yamelinno -f Containerfile .
```
This will build the container image with the name `yamelinno`. You can then run it as shown above.

# Coding guidelines
This project follows some coding guidelines to keep the codebase clean and easy to understand. Here are some of them:
- Use type hints whenever possible.
- Use docstrings to document functions and classes.
- Avoid using global variables, magic numbers, long one-liners, undefined behaviours and other bad practices.
- Avoid complexity whenever possible. That means no fancy algorithms, no fancy data structures, no fancy anything. It also means no super long functions or classes. Keep it simple, this is not Java.
- Prefer readability over performance. This tool is not meant to be used in performance-critical applications. Parsing errors are serious business, though.
- Name variables, functions, and classes in a way that makes their purpose clear.
- Write tests for every function and class. The goal is to have 100% coverage. No exceptions.
- If you feel like you are making your own programming language, you probably are. Don't do that, please.
- When in doubt, follow the zen of Python.

If you are willing to follow these guidelines, you are welcome to contribute to this project in any way you see fit. PRs, comments, bug reports and ideas are all welcome!

# Acknowledgements
This tool would not exist if there was no InnoSetup, and that's all thanks to the awesome people at https://jrsoftware.org/ (particularly Jordan Russell). Thanks for making it available for free, and for allowing the development of derivative works. 
You can check it out at the link above, it's a great piece of software.

# License
This tool is free software, and may be redistributed under the terms specified in the GNU General Public License version 3.0 (or later). See the LICENSE file for details.
