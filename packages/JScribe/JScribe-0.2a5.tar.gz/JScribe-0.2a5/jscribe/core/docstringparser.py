# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""*
@module jscribe.core.docstringparser
@author Rafał Łużyński
"""

import re
import codecs
import json
from collections import OrderedDict

from jscribe.utils.file import get_py_file_encoding
from jscribe.conf import settings


class DocStringParser(object):
    """* With this class you can collect documentation data from source files.

    Example usage:

    {$python
    filepaths = ['your/path/to/source.js', 'your/path/to/source2.js']
    dsp = DocStringParser(tag_settings, doc_string_regex, tag_regex)
    for path in filepaths:
        dsp.parse_file(path)
    dsp.data  # dictionary with your collected data
    $}

    Structure of collected data is described here:
        {#jscribe.core.docstringparser.DocStringParser.data}
    @class jscribe.core.docstringparser.DocStringParser
    """

    class TagValueException(Exception):
        """* Raised if wrong data is passed for tag.
        @exception .TagValueException
        """

    class InvalidDocStringException(Exception):
        """* Raised if wrong data is found in doc string.
        In example if two element tags were found.
        @exception .InvalidDocStringException
        """

    class InvalidTagException(Exception):
        """* Raised if tag that isn't defined is found.
        @exception .InvalidTagException
        """

    class InvalidElementPathException(Exception):
        """* Raised if invalid path to element is found.
        @exception .InvalidElementPathException
        """

    class TagSettingsException(Exception):
        """* Raised if wrong settings for tag are set.
        @exception .TagSettingsException
        """

    def __init__(self, tag_settings, doc_string_regex, tag_regex, ignore_invalid_tags=False):
        """* Initialization.
        @method .__init__
        @constructor
        @param self
        @param tag_settings {{dict}} - Dictionary with tag settings.
        @param doc_string_regex {{regex}} - Regex that matches doc strings.
        @param tag_regex {{regex}} - Regex that matches tags in doc strings.
        This regex should check if *tag sign* preceding characters are whitespaces, if not then it
        should not be matched.
        @param ignore_invalid_tags=False {{boolean}} - If `True` then invalid tag name won't raise
        error.
        """
        # map of tag property name and function to parse data from that tag string
        self.PROPERTY_TAGS = {
            'return': self._get_return_from_tag_string,
            'param': self._get_param_from_tag_string,
            'author': self._get_author_from_tag_string,
            'valtype': self._get_valtype_from_tag_string,
            'inherits': self._get_inherits_from_tag_string,
            'access': self._get_access_from_tag_string,
            'version': self._get_version_from_tag_string,
            'license': self._get_license_from_tag_string,
            'example': self._get_example_from_tag_string,
            'private': lambda ts: ('access', 'private'),
            'static': lambda ts: ('access', 'static'),
            'constructor': lambda ts: ('access', 'constructor'),
        }

        self._doc_string_regex = None
        self._doc_string_regex_obj = None
        self.doc_string_regex = doc_string_regex
        self._tag_regex = None
        self._tag_regex_obj = None
        self.tag_regex = tag_regex
        self.ignore_invalid_tags = ignore_invalid_tags
        self._tag_alias_map = {}
        self._tag_settings = tag_settings
        self._create_tag_alias_map(tag_settings)
        """* Dictionary with collected documentation data from source files.

        Structure of this dictionary: will be updated

        @valtype {{dict={'properties': {}}}}
        @attribute .data
        """
        self.data = OrderedDict({'properties': OrderedDict({})})
        self.documentation_filepaths = []
        self._temp_data = OrderedDict({})

    @property
    def doc_string_regex(self):
        return self._doc_string_regex

    @doc_string_regex.setter
    def doc_string_regex(self, doc_string_regex):
        """* Property method setter for doc_string_regex. By assigning new regex to it, it
        automaticaly compiles new regex instance.
        @property .doc_string_regex
        @valtype {{list|tuple}} - Two element long list or tuple, first must be a regex
            for doc string opening tag, second for closing.
        """
        self._doc_string_regex = doc_string_regex
        # only whitespaces before opening tag
        no_whitespace_regex = r'^\s*?'
        self._doc_string_open_regex_obj = re.compile(doc_string_regex[0])
        self._doc_string_open_whitespaces_regex_obj = re.compile(
            no_whitespace_regex + doc_string_regex[0]
        )
        self._doc_string_close_regex_obj = re.compile(doc_string_regex[1])

    @property
    def tag_regex(self):
        return self._tag_regex

    @tag_regex.setter
    def tag_regex(self, tag_regex):
        """* Property for tag_regex. By assigning new regex to it, it
        automaticaly compiles new regex instance.
        @property .tag_regex
        @valtype {{str}} - Regex string for tag.
        """
        self._tag_regex = tag_regex
        self._tag_regex_obj = re.compile(tag_regex, flags=re.MULTILINE)

    def _create_tag_alias_map(self, tag_settings):
        """* Creates map between tag name and its aliases.
        @method ._create_tag_alias_map
        @param self
        @private
        @param tag_settings {dict} - Dictionary with tag settings
        """
        for tag, _settings in tag_settings.iteritems():
            aliases = get_tag_type_property(tag_settings, _settings, 'alias')
            if aliases is None:
                continue
            for alias in aliases:
                self._tag_alias_map[alias] = tag

    def parse_file(self, path):
        """* Parses file from given path and collects documentation data from it.
        @method .parse_file
        @param self
        @param path {str} - path to source file
        """
        # get coding of source file
        source_coding = get_py_file_encoding(path)
        # get valid doc strings from file
        doc_strings = self._get_doc_strings(path, source_coding)
        if doc_strings:
            # append file path to documentation_filepaths only if at least one valid doc string
            # was found
            self.documentation_filepaths.append(path)
            previous_elements_paths = []
            # parse every doc string and get data from it
            for doc_string in doc_strings:
                doc_string_data = self._parse_doc_string(doc_string)
                if doc_string_data is None:
                    # that doc string is not a proper doc string
                    continue
                doc_string_data['filepath'] = path
                # adds collected data to temporary data collector from where data will be collected
                # to self.data
                previous_elements_paths = self._add_temp_data(
                    doc_string_data, previous_elements_paths
                )
            # collect data from temporary collector to self.data
            self._assemble_data()
        # if user wants then all discovered filepaths will be used in documentation source
        # generation
        if settings.ALL_SOURCE_FILES:
            self.documentation_filepaths.append(path)

    def _assemble_data(self):
        """* Method collects data from temporary collector and assembles it in `self.data`.
        @method ._assemble_data
        @param self
        @private
        """
        for path, data in self._temp_data.iteritems():
            path_parts = path.split('.')
            current_element = self.data
            for part in path_parts:
                if current_element['properties'].get(part) is None:
                    current_element['properties'][part] = {
                        'properties': OrderedDict({}),
                        'name': None,
                        'type': None,
                        'startline': None,
                        'endline': None,
                        'filepath': None,
                    }
                current_element = current_element['properties'].get(part)
            for prop in data:
                current_element[prop] = data[prop]

    def _add_temp_data(self, doc_string_data, previous_elements_paths):
        """* Adds collected data to temporary data collector from where data will be collected
        to `self.data`.
        @method ._add_temp_data
        @param self
        @param doc_string_data {dict} - Data collected from doc string
        @param previous_elements_paths {list}
        @private
        """
        name_parts = doc_string_data['name'].split('.')
        element_true_name = name_parts.pop(-1)
        if element_true_name == '':
            raise self.InvalidElementPathException('Invalid element path: {}'.format(
                doc_string_data['name']
            ))
        current_element_path = ''
        level = -1
        if len(name_parts) > 0 and name_parts[0] == '':
            # relative to previously defined elements
            for level, part in enumerate(name_parts):
                if part == '':
                    # relative
                    try:
                        current_element_path = previous_elements_paths[level]
                    except IndexError:
                        raise self.InvalidElementPathException('No parent element, path: {}'.format(
                            doc_string_data['name']
                        ))
                else:
                    # from here is the element path
                    ## check if rest of the path is valid
                    for part in name_parts[level:]:
                        if part == '':
                            raise self.InvalidElementPathException(
                                'Invalid element path: {}'.format(doc_string_data['name'])
                            )
                        current_element_path = '.'.join([current_element_path, part])
                    break
        elif len(name_parts) > 0 and name_parts[0] != '':
            # absolute path to element
            ## check if path is valid
            for part in name_parts:
                if part == '':
                    raise self.InvalidElementPathException('Invalid element path: {}'.format(
                        doc_string_data['name']
                    ))
            current_element_path = '.'.join(name_parts)
        # add element true name to path
        if current_element_path != '':
            current_element_path = '.'.join([current_element_path, element_true_name])
        else:
            current_element_path = element_true_name
        # add doc string data to temp data
        doc_string_data['name'] = element_true_name
        self._temp_data[current_element_path] = doc_string_data

        previous_elements_paths = previous_elements_paths [:level + 1]
        previous_elements_paths.append(current_element_path)
        return previous_elements_paths

    def _parse_doc_string(self, doc_string):
        doc_string_data = {
            'startline': doc_string[0],
            'endline': doc_string[1],
            'name': None,
            'type': None,
            'attributes': {},
        }
        # get description and tag strings
        tag_strings = []
        position_end = 0
        position_start = 0
        # while search position is less than doc string length
        while position_end < len(doc_string[2]):
            match_inst = self._tag_regex_obj.search(doc_string[2], position_end)
            if match_inst is None:
                # end of doc string
                position_end = len(doc_string[2])
                tag_strings.append(doc_string[2][position_start:])
            else:
                # found tag
                tag_strings.append(doc_string[2][position_start:match_inst.start()])
                position_start = match_inst.start()
                position_end = match_inst.end()
                # if tag has no value and is last in doc string
                if position_end >= len(doc_string[2]):
                    tag_strings.append(doc_string[2][position_start:position_end])

        # if tag_strings has only one element or less, then it's not a doc string (no tags in there)
        if len(tag_strings) < 2:
            return None
        # first element of tag_strings is a description of an element
        doc_string_data['description'] = tag_strings.pop(0).strip(' ').strip('\n').strip(' ')
        # indicates if doc string has element tag, it must have exactly one to be a valid doc string
        has_element_tag = False

        for tag_string in tag_strings:
            match_inst = self._tag_regex_obj.search(tag_string)
            tag_name = match_inst.group('tag')
            # check if tag type is valid
            ## check if tag is an element tag, check also aliases
            if self._tag_settings.get(tag_name) is not None or \
                    self._tag_alias_map.get(tag_name) is not None:
                if has_element_tag:
                    raise self.InvalidDocStringException(
                        'Two or more element tags in one doc string, docstring: {}.'.format(
                            doc_string
                        )
                    )
                has_element_tag = True
                if self._tag_settings.get(tag_name) is not None:
                    doc_string_data['type'] = tag_name
                elif self._tag_alias_map.get(tag_name) is not None:
                    doc_string_data['type'] = self._tag_alias_map.get(tag_name)
                # first word after tag name is an element name
                element_name, alias_name = self._get_element_name(tag_string)
                doc_string_data['name'] = element_name
                doc_string_data['alias_name'] = alias_name
            ## check if tag is a property tag
            elif self.PROPERTY_TAGS.get(tag_name) is not None:
                # get value of property from tag string
                tag_type, value = self.PROPERTY_TAGS.get(tag_name)(
                    tag_string[match_inst.end():]
                )
                # special case if tag is param
                if tag_type == 'param':
                    if doc_string_data['attributes'].get('params') is None:
                        doc_string_data['attributes']['params'] = []
                    doc_string_data['attributes']['params'].append(value)
                # special case if tag is example
                elif tag_type == 'example':
                    if doc_string_data['attributes'].get('examples') is None:
                        doc_string_data['attributes']['examples'] = []
                    doc_string_data['attributes']['examples'].append(value)
                else:
                    doc_string_data['attributes'][tag_type] = value
            ## tag type is invalid, raise exception if ignore invalid tags setting is not True
            elif not self.ignore_invalid_tags:
                raise self.InvalidTagException(
                    'Invalid tag "{}" in doc string: "{}".'.format(tag_name, doc_string[2])
                )

        if not has_element_tag:
            raise self.InvalidDocStringException(
                'No element tag in doc string.'
            )

        return doc_string_data

    def _get_element_name(self, tag_string):
        """* Returns element name (and alias_name if given) found in`tag_string`.
        @method ._get_element_name
        @private
        @param self
        @param tag_string {{unicode}} - Tag string where tag is an element.
        @return {{unicode, unicode}} - *element_name*, *alias_name*
        """
        tag_string_parts = tag_string.strip('\n').strip(' ').replace('\n', ' ').split(' ')
        try:
            element_name = tag_string_parts[1]
        except IndexError:
            raise self.TagValueException('No element name.')
        alias_name = None
        name_regex = r'"(?P<alias>.+?)"'
        match_inst = re.search(name_regex, tag_string, flags=re.DOTALL)
        if match_inst is not None:
            alias_name = match_inst.group('alias')
        if element_name == '':
            raise self.TagValueException('No element name.')
        return element_name, alias_name

    def _get_doc_strings(self, path, encoding):
        doc_strings = []
        # in doc string opening and closing tags
        in_tag = False
        doc_string_text = ''
        # line with whitespaces before doc string opening tag
        doc_string_intendation = 0
        with codecs.open(path, 'r', encoding) as f:
            for line_number, line in enumerate(f.readlines(), start=1):
                # if not in doc string opening and closing tags
                if not in_tag:
                    # find opening doc string tag with only whitespaces preceding
                    match_inst = self._doc_string_open_whitespaces_regex_obj.search(line)
                    if match_inst is not None:
                        # if opening tag is found, get position of opening tag without whitespaces
                        match_inst = self._doc_string_open_regex_obj.search(line)
                        in_tag = True
                        start_line = line_number
                        doc_string_intendation = match_inst.start()
                        doc_string_text += line[match_inst.end():].strip(' \t')
                    continue
                else:
                    # find closing doc string tag
                    match_inst = self._doc_string_close_regex_obj.search(line)
                    if match_inst is not None:
                        in_tag = False
                        end_line = line_number
                        text_line = line[:match_inst.start()]
                        text_line = text_line[doc_string_intendation:]
                        doc_string_text += text_line
                        doc_strings.append((start_line, end_line, doc_string_text))
                        doc_string_text = ''
                    else:
                        text_line = line
                        text_line = text_line[doc_string_intendation:]
                        if text_line == '':
                            text_line = '\n'
                        doc_string_text += text_line
                        continue
            f.close()
        return doc_strings

    def clear_data(self):
        """* Clears data.
        @method .clear_data
        @param self
        """
        self._temp_data = OrderedDict({})
        self.data = OrderedDict({'properties': OrderedDict({})})


    def data_json(self):
        return json.dumps(self.data)

    def _get_element_reference_from_value(self, val):
        ref = None
        ref_re_inst = re.search(r'^[{]#(?P<ref>.*?)[}]$', val)
        if ref_re_inst is not None:
            ref = ref_re_inst.group('ref')
        return ref

    def _get_author_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<author>.*?)$', tag_string, flags=re.DOTALL)
        if re_inst is not None:
            return 'author', re_inst.group('author').strip('\n').strip(' ')
        else:
            return 'author', ''

    def _get_return_from_tag_string(self, tag_string):
        re_inst = re.search(
            r'\s*?[{][{](?P<return_type>.*?)[}][}]\s-?[ ]?(?P<description>.*?)$',
            tag_string,
            flags=re.DOTALL
        )
        if re_inst is not None:
            ref = None
            if re_inst.group('return_type') is not None:
                val_brackets = '{' + re_inst.group('return_type') + '}'
                ref = self._get_element_reference_from_value(val_brackets)
            return 'return', {
                'type': {
                    'type': re_inst.group('return_type'),
                    'ref': ref,
                },
                'description': re_inst.group('description')
            }
        else:
            return 'return', None

    def _get_param_from_tag_string(self, tag_string):
        re_inst = re.search(
            r'\s*?(?P<name>\w+)' +
            r'(?:(?:=(?P<default>[^.]+?))|(?:(?P<seq>[.]{3}))|(?:))' +
            r'(?:\s[{][{](?P<type>.+?)[}][}])?' +
            r'(?:\s-?\s?(?P<desc>.*?))$',
            tag_string,
            flags=re.DOTALL
        )
        if re_inst is not None:
            ref = None
            if re_inst.group('type') is not None:
                val_brackets = '{' + re_inst.group('type') + '}'
                ref = self._get_element_reference_from_value(val_brackets)
            return 'param', {
                'name': re_inst.group('name'),
                'default': re_inst.group('default'),
                'is_sequenced': re_inst.group('seq'),
                'type': {
                    'type': re_inst.group('type'),
                    'ref': ref,
                },
                'description': re_inst.group('desc'),
            }
        else:
            raise self.TagValueException('Wrong data passed to param tag: "{}"'.format(tag_string))

    def _get_valtype_from_tag_string(self, tag_string):
        re_inst = re.search(
            r'\s*?[{][{](?P<valtype>.*?)(?:=(?P<default>.+?))?[}][}](?:\s-?\s?(?P<desc>.*?))$',
            tag_string,
            flags=re.DOTALL
        )
        val_brackets = '{' + re_inst.group('valtype') + '}'
        ref = self._get_element_reference_from_value(val_brackets)
        if re_inst is not None:
            return 'valtype', {
                'valtype': re_inst.group('valtype'),
                'ref': ref,
                'default': re_inst.group('default'),
                'description': re_inst.group('desc'),
            }
        else:
            raise self.TagValueException(
                'Wrong data passed to valtype tag: "{}"'.format(tag_string)
            )

    def _get_inherits_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?[{][{](?P<inherits>.*?)[}][}](\s|$)', tag_string)
        if re_inst is not None:
            val_brackets = '{' + re_inst.group('inherits') + '}'
            ref = self._get_element_reference_from_value(val_brackets)
            return 'inherits', {
                'inherits': re_inst.group('inherits'),
                'ref': ref,
            }
        else:
            raise self.TagValueException(
                'Wrong data passed to inherits tag: "{}"'.format(tag_string)
            )

    def _get_access_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<access>.*?)(\s|$)', tag_string)
        if re_inst is not None:
            return 'access', re_inst.group('access')
        else:
            raise self.TagValueException(
                'Wrong data passed to access tag: "{}"'.format(tag_string)
            )

    def _get_version_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<version>.*?)$', tag_string, flags=re.DOTALL)
        if re_inst is not None:
            return 'version', re_inst.group('version').strip('\n').strip(' ')
        else:
            return 'version', None

    def _get_license_from_tag_string(self, tag_string):
        re_inst = re.search(r'\s*?(?P<license>.*?)$', tag_string, flags=re.DOTALL)
        if re_inst is not None:
            return 'license', re_inst.group('license').strip('\n').strip(' ')
        else:
            return 'license', None

    def _get_example_from_tag_string(self, tag_string):
        re_inst = re.search(
            r'\s*?(?P<title>.+?)' +
            r'(?:\s[#](?P<langid>\w+?))?\s[{][$](?P<code>.*?)[$][}](?:\s(?P<desc>.*?))$',
            tag_string,
            flags=re.DOTALL
        )
        if re_inst is not None:
            return 'example', {
                'code': re_inst.group('code'),
                'description': re_inst.group('desc').strip('\n').strip(' '),
                'title': re_inst.group('title').strip('\n').strip(' '),
                'langid': re_inst.group('langid'),
            }
        else:
            raise self.TagValueException(
                'Wrong data passed to example tag: "{}"'.format(tag_string)
            )


def get_tag_type_property(tag_settings, tag_type, property_name):
    """* Gets tag property from settings.
    @function jscribe.core.docstringparser.get_tag_type_property
    @param tag_settings {{dict}}
    @param tag_type {{dict}}
    @param property_name {{str}}
    """
    prop = tag_type.get(property_name)
    if prop is None:
        parent_type = get_tag_parent_type(tag_settings, tag_type)
        if parent_type is None:
            raise DocStringParser.TagSettingsException(
                'No {} property on tag {}.'.format(property_name, tag_type.get('name'))
            )
        prop = get_tag_type_property(tag_settings, parent_type, property_name)
    return prop


def get_tag_parent_type(tag_settings, tag_type):
    """* Gets tag settings from parent tag type.
    @function jscribe.core.docstringparser.get_tag_parent_type
    @param tag_settings {{dict}}
    @param tag_type {{dict}}
    """
    parent_type_name = tag_type.get('parent_type')
    if parent_type_name is None:
        return None
    else:
        parent_type = tag_settings.get(parent_type_name)
        if parent_type is None:
            raise DocStringParser.TagSettingsException('Parent type "{}" doesn\'t exist'.format(
                parent_type_name
            ))
        return parent_type
