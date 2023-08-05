# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""*
@module jscribe.core.generator
"""


class Generator(object):
    """* Abstract Generator class. Inherit from this if you want to create your own generator.
    Look at the {#jscribe.generators.html.htmldefaultgenerator.HTMLDefaultGenerator} if you need
    help with creating generator.
    @class jscribe.core.generator.Generator
    """
    class GeneratorException(Exception):
        """* Raises if generator does something wrong.
        @exception .GeneratorException
        """
    class InvalidGeneratorException(Exception):
        """* Raises if used generator doesn't exist.
        @exception .InvalidGeneratorException
        """


"""*

##Will be updated. Sorry.##

If you have any question, email me at: rafalluzynski@prosaur.com

@manual generatorstemplates "6. Generators and templates"
"""