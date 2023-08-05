# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Settings module that should be imported whenever you need access to settings.

@module jscribe.conf.settings
"""

import sys
import json

from jscribe.conf.defaults import *


def load(path):
    """* Load settings from json file and assing every property of these settings to settings
    module.
    @function .load
    @param path {{str}}
    """
    with open(path, 'r') as f:
        _settings = json.load(f)
        f.close()
    for attr, value in _settings.iteritems():
        setattr(sys.modules[__name__], attr, value)


# MANUAL - SETTINGS FILE
"""* You have to create your own settings file to generate documentation and
pass path to it as first argument to {#jscribeit}.

File has to be in json format.

Example settings file (defaults):

{$json
{
    "INPUT_PATHS": ["./"],
    "IGNORE_PATHS_REGEX": [],
    "FILE_REGEX": ".*?[.]js$",
    "FILE_IGNORE_REGEX": null,
    "DOCUMENTATION_OUTPUT_PATH": "./",
    "DOC_STRING_REGEX": ["[/][*][*]", "(?<!\\\\)[*][/]"],
    "TAG_REGEX": "^\\s*?[@](?P<tag>.*?)\\s",
    "IGNORE_INVALID_TAGS": false,
    "TEMPLATE": "default",
    "TEMPLATE_SETTINGS": {
        "SHOW_LINE_NUMBER": true,
        "FOOTER_TEXT": "Footer text",
        "TITLE": "My Docs Title",
        "ELEMENT_TEMPLATES": {}
    },
    "TAG_SETTINGS": "jscribe.conf.jstagsettings",
    "OUTPUT_ENCODING": "utf-8",
    "LANGUAGE": "javascript",
    "GENERATOR": "html",
    "ALL_SOURCE_FILES": false
}
$}

###Fields:###

- **INPUT_PATHS**: array of paths to directories that contains your source files you want to be
discovered
- **IGNORE_PATHS_REGEX**: array of regexes that match paths to directories that you want to exclude
from your INPUT_PATHS, in example unit tests files.
- **FILE_REGEX**: regex that matches source file names that should be discovered
- **FILE_IGNORE_REGEX**: regex that matches source file names that must not be discovered
- **DOCUMENTATION_OUTPUT_PATH**: path to fir where you want to create documentation files
- **DOC_STRING_REGEX**: array with two regexes, first match opening tag of doc string in source files,
    second matches closing tag, for javascript these tags are usually [`/**`, `*/`],
    for python (without backslash)[`\"""`, `\"""`], but I use [`\"""*`, `\"""`] for few cases when someone wants to
    use multiline string as value. By the way, doc string is found only if opening tag is preceeded
    but nothing except whitespaces. In regex you should also check if escape character `\` isn't
    preceding closing doc string tag. Thanks to taht you can place closing tag inside your doc
    string, just like I did in this doc string.
- **TAG_REGEX**: regex that matches property tags in doc strings, you should not edit this until you
    know what you are doing, usually it matches syntax `@property_name`
- **IGNORE_INVALID_TAGS**: if `true` then if you provide invalid tag property name in doc string, error
    won't be raised
- **TEMPLATE**: name of template that is installed in `jscribe/templates/{generator_name}` package, in
    example `default` template, if generator is `html` points to `jscribe/templates/html/default/`
- **TEMPLATE_SETTINGS**: settings that are different for every template, will be described in template
    section
- **TAG_SETTINGS**: path to file with your tag settings, this can be a path to python package or path
    to json file. You can use one of builtin tag settings: `jscribe.conf.pythontagsettings`,
    `jscribe.conf.jstagsettings` or your own, I admit that you create your own tag settings file.
    How to do that is described in {#tagsettings}.
- **OUTPUT_ENCODING**: how documentation output files should be encoded
- **LANGUAGE**: langauge that will be used for syntax color while creating source documentation files,
    it will be also used in code snippets by default if you won't provide language explicitly.
    Pass here name of lexer used by pygments, in example: python, javascript, bash etc.
- **GENERATOR**: generator that will be used for creating documentation, right now only *html* is
    supported
- **ALL_SOURCE_FILES**: if `true` then source file documentation will be created for all discovered
    source files

**You don't have to set all properties in your settings because if you don't then default will be
taken.**

@manual settings "3. Settings file"
"""
