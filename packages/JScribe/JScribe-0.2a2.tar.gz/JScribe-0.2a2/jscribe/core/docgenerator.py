# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""*
@module jscribe.core.docgenerator
@author Rafał Łużyński
"""

import json
import importlib

from jscribe.utils.file import discover_files
from jscribe.conf import settings
from jscribe.core.docstringparser import DocStringParser
from jscribe.core.htmldocgenerator import HTMLDocumentationGenerator
from jscribe.core.generator import Generator


class DocumentationGenerator(object):
    """* This is the main class of JScribe.

    Create instance of this class and call
        {#jscribe.core.docgenerator.DocumentationGenerator.generate_documentation}
        to create documentation.
    @class jscribe.core.docgenerator.DocumentationGenerator
    """

    """* Map of generator names and its coresponding classes. If you add new generator to JScribe
        then you have to add it here also.
        @attribute .GENERATORS
        @valtype {{dict={ 'html': HTMLDocumentationGenerator}}}
    """
    GENERATORS = {
        'html': HTMLDocumentationGenerator,
    }
    def __init__(self, settings_path):
        """* Init. Internally calls
            {#jscribe.core.docgenerator.DocumentationGenerator._get_doc_data}
        so doc data is collected on initialize.
        @constructor
        @method .__init__
        @param self
        @param settings_path {{unicode}} - Path to settings file (json).
        """
        # here documentation data will be collected
        self.doc_data = {}
        self.tag_settings = {}
        self.discovered_filepaths = []
        # load settings from file into jscribe.conf.settings module
        settings.load(settings_path)
        self._load_tag_settings(settings.TAG_SETTINGS)
        # collect documentation data from discovered source files
        self._get_doc_data()

    def _load_tag_settings(self, tag_settings_path):
        """* Load tag settings from file.

        If given `tag_settings_path` is python module then it imports `TAG_SETTINGS`
        attribute from that module. If it's json file, then loads data from that file.
        @method ._load_tag_settings
        @param self
        @param tag_settings_path {{str}} - Path to json file or python module path.
        @private
        """
        # check if file is json
        if tag_settings_path.split('.')[-1] == 'json':
            with open(tag_settings_path, 'r') as f:
                self.tag_settings = json.load(f)
                f.close()
        else:
            # if file is not json then assume it's a path to python module
            self.tag_settings = getattr(
                importlib.import_module(
                    tag_settings_path
                ),
                'TAG_SETTINGS'
            )

    def _get_doc_data(self):
        """* Discovers source files paths (basing on paths and regexes in settings)
            and collects documentation data from it.
        @method ._get_doc_data
        @param self
        @private
        """
        # get list of source file paths
        self.discovered_filepaths = discover_files(
            settings.INPUT_PATHS, settings.FILE_REGEX,
            ignore_paths_regex=settings.IGNORE_PATHS_REGEX,
            ignore_regex=settings.FILE_IGNORE_REGEX
        )
        # create file parser with settings given by user
        dsp = DocStringParser(
            self.tag_settings, settings.DOC_STRING_REGEX, settings.TAG_REGEX,
            settings.IGNORE_INVALID_TAGS
        )
        # parse every discovered source file
        for filepath in self.discovered_filepaths:
            dsp.parse_file(filepath)
        # get collected data
        self.doc_data = dsp.data
        # get filepaths from which source documentation will be created
        # (documentation files with source code and colour syntax)
        # this list is a subset of self.discovered_filepaths, since only filepaths where
        # defined elements were found are passed (unless you specify otherwise in settings)
        self.documentation_filepaths = dsp.documentation_filepaths

    def generate_documentation(self):
        """* Generates documentation using given in settings generator class and collected doc data.
        @method .generate_documentation
        @param self
        """
        # get generator
        generator_class = self.GENERATORS.get(settings.GENERATOR)
        if generator_class is None:
            raise Generator.InvalidGeneratorException(
                'Invalid generator "{}". Maybe not supported yet.'.format(settings.GENERATOR)
            )
        # make instance of generator and generate docs
        generator = generator_class(self.doc_data, self.tag_settings, self.documentation_filepaths)
        generator.generate_documentation()

