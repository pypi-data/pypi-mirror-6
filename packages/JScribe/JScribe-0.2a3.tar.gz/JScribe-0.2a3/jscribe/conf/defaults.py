# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Default settings for jscribe.
@module jscribe.conf.defaults
"""

INPUT_PATHS = ["./"]  # paths to source files that should be discovered
IGNORE_PATHS_REGEX = []
FILE_REGEX = r".*?[.]js$"
FILE_IGNORE_REGEX = None
DOCUMENTATION_OUTPUT_PATH = "./"
DOC_STRING_REGEX = [r"[/][*][*]", r"(?<!\\)[*][/]"]
TAG_REGEX = r"^\s*?[@](?P<tag>.*?)\s"
IGNORE_INVALID_TAGS = False
TEMPLATE = "default"
TEMPLATE_SETTINGS = {
        "SHOW_LINE_NUMBER": True,
        "FOOTER_TEXT": "Footer text",
        "TITLE": "My Docs Title",
        "ELEMENT_TEMPLATES": {},
}
TAG_SETTINGS_PATH = "jscribe.conf.jstagsettings"
OUTPUT_ENCODING = "utf-8"
LANGUAGE = "javascript"
GENERATOR = "html"
ALL_SOURCE_FILES = False
