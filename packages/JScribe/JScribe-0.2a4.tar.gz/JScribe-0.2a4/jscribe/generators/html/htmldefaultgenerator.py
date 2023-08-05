# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""*
@module jscribe.generators.html.htmldefaultgenerator
"""

import os
import re
import codecs
import logging
import importlib
import shutil
from collections import OrderedDict

from markdown import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from jscribe.utils.file import get_py_file_encoding
from jscribe.core.generator import Generator
from jscribe.conf import settings
from jscribe.core.jinjatemplaterenderer import JinjaTemplateRenderer
from jscribe.core.docstringparser import DocStringParser, get_tag_type_property


class HTMLDefaultGenerator(Generator):
    """* Default doc generator for HTML output.

    @class jscribe.generators.html.htmldefaultgenerator.HTMLDefaultGenerator
    @inherits {{#jscribe.core.generator.Generator}}
    """
    def __init__(self, template_settings, doc_data, tag_settings, discovered_filepaths):
        """* Initialization.
        @method .__init__
        @param self
        @param template_settings {{dict}}
        @param doc_data {{dict}}
        @param tag_settings {{dict}}
        @param discovered_filepaths {{list}}
        """
        self.doc_data = doc_data
        self.tag_settings = tag_settings
        self.template_settings = template_settings
        self.discovered_filepaths = discovered_filepaths
        self.renderer = self.create_renderer()

    def get_template_for_element(self, tag_type_name):
        return self.template_settings['ELEMENT_TEMPLATES'].get(
            tag_type_name, self.template_settings['ELEMENT_TEMPLATES'].get('default')
        )

    def _make_url_from_namepath(self, namepath):
        name_parts = namepath.split('.')
        if name_parts[0] == '':
            raise DocStringParser.InvalidElementPathException(
                u'Only absolute namepaths can be passed. Namepath: {}'.format(namepath)
            )
        current_element = self.doc_data
        current_name_url = ''
        anchor_url = ''
        separate_url = None
        for part in name_parts:
            if part == '':
                raise DocStringParser.InvalidElementPathException(
                    u'Invalid element path: {}'.format(namepath)
                )
            current_element = current_element['properties'].get(part)
            if current_element is None:
                raise DocStringParser.InvalidElementPathException(
                    u"Element does not exist: {}".format(namepath)
                )
            if current_name_url:
                current_name_url = '_'.join([current_name_url, part])
            else:
                current_name_url = part
            if not self._is_element_defined(current_element):
                anchor_url = ''
                separate_url = current_name_url
            elif not current_element['is_separate']:
                if anchor_url:
                    anchor_url = '_'.join([anchor_url, part])
                else:
                    anchor_url = part
            else:
                anchor_url = ''
                separate_url = current_name_url
        if not self._is_element_defined(current_element):
            raise DocStringParser.InvalidElementPathException(
                u"Can't reference not defined element: {}".format(namepath)
            )
        if separate_url is None:
            raise Generator.GeneratorException(
                u'Defined element is not separate nor assigned to any separate element. ' +
                u'Namepath: {}'.format(namepath)
            )
        url = '.'.join([separate_url, 'html'])
        if anchor_url:
            url = '#'.join([url, anchor_url])
        return url, anchor_url

    def get_path_to_sourcefile(self, filepath):
        return '.'.join([filepath.replace(os.path.sep, '_')[1:], 'html'])

    def get_path_to_list_file(self, list_type):
        return '.'.join(['list_{}'.format(list_type), 'html'])

    def generate_documentation(self):
        # get documentation data for templates
        self._build_template_data()
        # sort lists by order
        self.doc_data['lists'] = OrderedDict(
            sorted(self.doc_data['lists'].items(), key=lambda v: v[1]['order'])
        )
        # add lists to the global context so its always available to mainframe
        self.renderer.update_globals({'lists': self.doc_data['lists']})
        # create source doc files (source code with line numbers and anchors)
        self.generate_source_files_for_documentation()
        # create list files
        self.generate_list_files(self.doc_data)
        # create files for every element with separate type
        for prop, element in self.doc_data['root_element'].get('properties').iteritems():
            # check if element is defined in documentation
            if not self._is_element_defined(element):
                self._check_if_properties_are_separate(element)
            # check if element is separate, only then create file
            if element.get('is_separate'):
                self.generate_element_file(element)
            else:
                self._check_if_properties_are_separate(element)
        # copy style file
        self._copy_template_style_file()

    def _is_element_defined(self, element):
        if element.get('type') is None:
            return False
        return True

    def create_renderer(self):
        template_package = 'jscribe.templates.{}.{}'.format(settings.GENERATOR, settings.TEMPLATE)
        renderer = JinjaTemplateRenderer(
            template_package,
            {
                'tag_settings': self.tag_settings,
                'render_element': self.render_element,
                'render_element_contents': self.render_element_contents,
                'FOOTER_TEXT': self.template_settings['FOOTER_TEXT'],
                'TITLE': self.template_settings['TITLE'],
            }
        )
        return renderer

    def _copy_template_style_file(self):
        css_style_name = 'style.css'
        template_package = importlib.import_module(
            'jscribe.templates.{}.{}'.format(settings.GENERATOR, settings.TEMPLATE)
        )
        style_path = os.path.join(
            os.path.dirname(os.path.abspath(template_package.__file__)),
            css_style_name
        )
        style_dst_path = os.path.join(
            settings.DOCUMENTATION_OUTPUT_PATH, css_style_name
        )
        shutil.copy(style_path, style_dst_path)

    def _build_template_data(self):
        lists = {}
        namepath = ''
        # prepare elements data before converting
        self._prepare_element_data(self.doc_data)
        # convert elements data
        for prop, element in self.doc_data.get('properties').iteritems():
            # set namepath for element
            if self._is_element_defined(element):
                # if element is not defined but is used in namepath somewhere
                element['name'] = prop
            namepath = element.get('name')
            element['namepath'] = namepath
            element, lists = self._convert_element_data(element, lists)
            self._get_element_template_data(element, namepath, lists)
        lists = self._sort_list_elements(lists)
        self.doc_data = {'root_element': self.doc_data, 'lists': lists}

    def _sort_list_elements(self, lists):
        for _list in lists.values():
            _list['elements'] = sorted(
                _list['elements'], key=self._compare_elements_for_list_sorting
            )
        return lists

    def _compare_elements_for_list_sorting(self, element):
        if element.get('alias_name', None) is not None:
            return element.get('alias_name', None)
        return element.get('name', None)

    def _prepare_element_data(self, element):
        for element in element.get('properties').values():
            if self._is_element_defined(element):
                # get element tag type settings
                tag_type_name = element.get('type')
                tag_type = self.tag_settings.get(tag_type_name)
                # set tag type_name
                type_name = get_tag_type_property(self.tag_settings, tag_type, 'name')
                element['type_name'] = type_name
                # set tag type title
                type_title = get_tag_type_property(self.tag_settings, tag_type, 'title')
                element['type_title'] = type_title
                # set source_visible property
                source_visible = get_tag_type_property(self.tag_settings, tag_type, 'source_visible')
                element['source_visible'] = source_visible
                # set is callable property
                is_callable = get_tag_type_property(self.tag_settings, tag_type, 'callable')
                element['is_callable'] = is_callable
                # set source_visible property
                source_visible = get_tag_type_property(self.tag_settings, tag_type, 'source_visible')
                element['source_visible'] = source_visible
                # check if element is separate
                is_separate = get_tag_type_property(self.tag_settings, tag_type, 'separate')
                element['is_separate'] = is_separate
            self._prepare_element_data(element)

    def _get_element_template_data(self, data, namepath, lists):
        for prop, element in data.get('properties').iteritems():
            # set namepath for element
            if element.get('name') is None:
                # if element is not defined but is used in namepath somewhere
                element['name'] = prop
            _namepath = '.'.join([namepath, element.get('name')])
            element['namepath'] = _namepath
            element, lists = self._convert_element_data(element, lists)
            self._get_element_template_data(element, _namepath, lists)

    def _convert_element_data(self, element, lists):
        if self._is_element_defined(element):
            # convert references to elements, to html links
            element = self._convert_references(element)
            # convert inline code blocks into html parsed code
            element = self._convert_element_code_blocks(element)
            # convert markup in description into html, THIS MUST BE DONE AFTER CONVERTING REST
            # "PARTS" OF DESCRIPTION, LIKE REFERENCES OR CODE BLOCKS
            element = self._convert_element_descriptions_markup(element)
            # convert code examples
            element = self._convert_code_examples(element)
            output_path, url_id = self._make_url_from_namepath(element.get('namepath'))
            element['doc_element_path'] = output_path
            element['doc_element_id'] = url_id
            # get element tag type settings
            tag_type_name = element.get('type')
            tag_type = self.tag_settings.get(tag_type_name)
            # add element to its element list
            if lists.get(tag_type_name) is None:
                order = get_tag_type_property(self.tag_settings, tag_type, 'list_order')
                lists[tag_type_name] = {
                    'path': self.get_path_to_list_file(tag_type_name), 'elements': [],
                    'order': order,
                }
            lists[tag_type_name]['elements'].append(element)
            # remove beginnig dot from filepath, that os.walk leaves there
            element['filepath'] = element['filepath'][1:]
            # set element path to sourcefile
            element['sourcepath'] = self.get_path_to_sourcefile(element.get('filepath'))
        return element, lists

    def _convert_code_examples(self, element):
        # convert code examples to parsed code
        if element['attributes'].get('examples') is not None:
            for example in element['attributes']['examples']:
                langid = settings.LANGUAGE
                if example.get('langid') is not None:
                    langid = example.get('langid')
                example['langid'] = langid
                example['code_html'] = self._convert_code(example['code'], langid)
        return element

    def _convert_element_descriptions_markup(self, element):
        # convert element description from markdown to html
        element['description_html'] = self._convert_markup(element['description'])
        # convert parameter descriptions if are set
        if element['attributes'].get('params') is not None:
            for param in element['attributes']['params']:
                param['description_html'] = self._convert_markup(param['description'])
        # convert return description if is set
        if element['attributes'].get('return') is not None:
            element['attributes']['return']['description_html'] = self._convert_markup(
                element['attributes']['return']['description']
            )
        # convert valtype description if is set
        if element['attributes'].get('valtype') is not None:
            element['attributes']['valtype']['description_html'] = self._convert_markup(
                element['attributes']['valtype']['description']
            )
        # convert example descriptions if are set, and convert code to html with pygments
        if element['attributes'].get('examples') is not None:
            for example in element['attributes']['examples']:
                example['description_html'] = self._convert_markup(example['description'])
        return element

    def _convert_element_code_blocks(self, element):
        description = element['description']
        matches = re.finditer(
            r'(?P<wrap>[{][$](?P<lang>\w*?)\s(?P<code>.*?)[$][}])', description, flags=re.DOTALL
        )
        len_diff = 0
        for match in matches:
            code = match.group('code')
            lang = match.group('lang')
            langid = settings.LANGUAGE
            if lang:
                langid = lang
            code_html = self._convert_code(u'\t\r\n' + code, langid)
            description = (
                description[0:match.start('wrap') + len_diff] +
                code_html +
                description[match.end('wrap') + len_diff:]
            )
            len_diff -= match.end('wrap') - match.start('wrap')
            len_diff += len(code_html)
        element['description'] = description
        return element

    def _convert_references(self, element):
        description = element['description']
        matches = re.finditer(r'(?P<wrap>[{]#(?P<ref>.*?)[}])', description)
        len_diff = 0
        for match in matches:
            url, url_id = self._make_url_from_namepath(match.group('ref'))
            link = self._make_link(url, match.group('ref'))
            description = (
                description[0:match.start('wrap') + len_diff] +
                link +
                description[match.end('wrap') + len_diff:]
            )
            len_diff -= match.end('wrap') - match.start('wrap')
            len_diff += len(link)
        element['description'] = description
        params = element['attributes'].get('params')
        if params is not None:
            for param in params:
                if param['type']['ref'] is not None:
                    url, url_id = self._make_url_from_namepath(param['type']['ref'])
                    param['type']['ref_html'] = self._make_link(url, param['type']['ref'])
        inherits = element['attributes'].get('inherits')
        if inherits is not None:
            if inherits['ref'] is not None:
                url, url_id = self._make_url_from_namepath(inherits['ref'])
                inherits['ref_html'] = self._make_link(url, inherits['ref'])
        returns = element['attributes'].get('return')
        if returns is not None:
            if returns['type']['ref'] is not None:
                url, url_id = self._make_url_from_namepath(returns['type']['ref'])
                returns['type']['ref_html'] = self._make_link(url, returns['type']['ref'])
        valtype = element['attributes'].get('valtype')
        if valtype is not None:
            if valtype['ref'] is not None:
                url, url_id = self._make_url_from_namepath(valtype['ref'])
                valtype['ref_html'] = self._make_link(url, valtype['ref'])
        return element

    def _make_link(self, url, title):
        #markdown_link = u'[{0}]({1} "{0}")'.format(title, url)
        #return markdown(markdown_link, output_format='html5')
        link = u'<a href="{1}" title="{0}">{0}</a>'.format(title, url)
        return link

    def _convert_code(self, code, langid):
        lexer = get_lexer_by_name(langid, stripall=True)
        formatter = HtmlFormatter(
            linenos=self.template_settings['SHOW_LINE_NUMBER'],
            cssclass="source_{}".format(langid), linespans='line'
        )
        return highlight(code, lexer, formatter)

    def  _convert_markup(self, markup_string):
        return markdown(
            markup_string,
            output_format='html5',
        )

    def generate_element_file(self, element_data):
        for prop, element in element_data.get('properties').iteritems():
            # check if element is defined in documentation
            if not self._is_element_defined(element):
                self._check_if_properties_are_separate(element)
                continue
            if element.get('is_separate'):
                self.generate_element_file(element)
            else:
                self._check_if_properties_are_separate(element)
        result = self.render_element(element_data)
        self.renderer.render_to_file(
            'element.html',
            {'element_rendered': result, 'element': element_data, },
            os.path.join(settings.DOCUMENTATION_OUTPUT_PATH, element_data['doc_element_path']),
            settings.OUTPUT_ENCODING
        )
        logging.info('Created: {}'.format(element_data['doc_element_path']))

    def _check_if_properties_are_separate(self, element_data):
        for prop, element in element_data.get('properties').iteritems():
            # check if element is defined in documentation
            if not self._is_element_defined(element):
                self._check_if_properties_are_separate(element)
            if element.get('is_separate'):
                self.generate_element_file(element)
            else:
                self._check_if_properties_are_separate(element)

    def generate_list_files(self, doc_data):
        for list_type, _list in doc_data['lists'].iteritems():
            self.renderer.render_to_file(
                'list.html',
                {'list': _list, 'list_type': list_type, },
                os.path.join(
                    settings.DOCUMENTATION_OUTPUT_PATH,
                    self.get_path_to_list_file(list_type)
                ),
                settings.OUTPUT_ENCODING
            )

    def generate_source_files_for_documentation(self):
        for filepath in self.discovered_filepaths:
            encoding = get_py_file_encoding(filepath)
            with codecs.open(filepath, 'r', encoding) as f:
                code = f.read()
                f.close()
            output_path = self.get_path_to_sourcefile(filepath[1:])
            lexer = get_lexer_by_name(settings.LANGUAGE, stripall=True)
            formatter = HtmlFormatter(
                linenos=self.template_settings['SHOW_LINE_NUMBER'],
                cssclass="source_{}".format(settings.LANGUAGE), linespans='line'
            )
            result = highlight(code, lexer, formatter)
            self.renderer.render_to_file(
                'sourcefile.html',
                {'source': result, },
                os.path.join(settings.DOCUMENTATION_OUTPUT_PATH, output_path),
                settings.OUTPUT_ENCODING
            )
            logging.info('Created: {}'.format(output_path))

    def render_element(self, element):
        template = self.get_template_for_element(element.get('type'))
        return self.renderer.render(template, {'element': element, })

    def render_element_contents(self, element):
        template = 'element_contents.html'
        return self.renderer.render(template, {'element': element, })
