# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""*
@module jscribe.core.jinjatemplaterenderer
@author Rafał Łużyński
"""

from jinja2 import Environment, PackageLoader


class JinjaTemplateRenderer(object):
    """* Jinja template renderer.
    Creates html files basing on templates with Jinja2 syntax.
    @class jscribe.core.jinjatemplaterenderer.JinjaTemplateRenderer
    """
    def __init__(self, template_package, global_context):
        """* HTML format generator.
        @method .__init__
        @param self
        @param template_package {{str}} - Python path to template package
        @param global_context {{dict}} - Dictionary with values that will be available everywhere
            in templates.
        @constructor
        """
        # setup jinja template engine
        self.env = Environment(
            loader=PackageLoader(template_package, 'templates'),
            extensions=['jinja2.ext.i18n']
        )
        self.env.globals = global_context

    def update_globals(self, new_globals):
        """* Update template globals dictionary with new dict.
        @method .update_globals
        @param self
        @param new_globals {{dict}}
        """
        self.env.globals.update(new_globals)

    def render_to_file(self, template, context, filepath, encoding):
        """* Creates new html file with given parameteres.
        @method .render_to_file
        @param self
        @param template {{str}} - template file in choosen template package
        @param context {{dict}} - Dictionary with data for template
        @param filepath {{str}} - Where new file will be created
        @param encoding {{str}} - Encoding in which new file will be encoded
        """
        self.env.get_template(template).stream(context).dump(filepath, encoding=encoding)

    def render(self, template, context):
        """* Returns rendered template.
        @method .render
        @param self
        @param template {{str}} - template file in choosen template package
        @param context {{dict}} - Dictionary with data for template
        @return {unicode} - Rendered file
        """
        return self.env.get_template(template).render(context)
