# yamelinno
A tool to render yaml into InnoSetup iss files.

# Why?
I wanted to have a way to define my InnoSetup scripts in a more structured, reusable way, and I like yaml. I also happen to dislike a lot the InnoSetup scripting language, so I wanted to avoid it as much as possible. This tool is the result of that.

## Seriously, why?
Well, it was a fun project to work on, and I think it can be useful for some people. I also wanted to learn how to write a parser without using either Jinja or a super complex architecture, keeping it simple and easy to understand was in itself a challenge. 
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
yamelinno [options] <input_yml_file>

Options:
  -o, --output <output_file>  Output file. If not specified, the output will be printed to stdout.
  -s, --schema <schema_file>  Schema file. If not specified, the schema will be read from "schema.yml", which must be in the same directory as the input file.
  -v, --version               Display the version of the tool.
  -h, --help                  Display this help message.
```

# Example
```yaml
# input.yml
setup:
  appId: "2b6f0cc904d137be2e1730235f5664094b831186" #UUID: 
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
AppId=2b6f0cc904d137be2e1730235f5664094b831186
AppName=MyApp
AppVersion=1.0

[Files]
Source: "src/main.js"; DestDir: "{app}"; Flags: ignoreversion

```

## Explanation
The tool reads the input file and validates it against the schema. If the input file is valid, it renders the iss file. The schema is used to validate the input file and to provide hints to the user. The schema is also a yaml file, so you can modify it to add missing keys or entries without having to modify the tool. The attributes and structure of the schema are pretty much self-explanatory, but here is a brief explanation of the keys:

- `renderedName`: The name of the key in the rendered iss file.
- `children`: The type of the key. It can be `keys` or `entries`. `keys` are used to define a dictionary, while `entries` are used to define a list of dictionaries (which follow the same schema that is defined in the `entry` key).

## Roadmap
- [] More InnoSetup directives in the base schema.
- [] Support for snippets, which are reusable code blocks that can be included in the yaml file.
- [] Support for brief syntax, which would allow the user to write the yaml file in a more concise way.
- [] Support for templates that can be resolved at runtime, either by the tool or by the user.
- [] Enable usage as a library, so it can be integrated with other tools.
- [] Port to Rust, because why not?

## License
This tool is free software, and may be redistributed under the terms specified in the GNU General Public License version 3.0 (or later). See the LICENSE file for details.