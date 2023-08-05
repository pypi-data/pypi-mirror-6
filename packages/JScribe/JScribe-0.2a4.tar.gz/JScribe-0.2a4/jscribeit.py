#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""* Generates documentation from source code, that your settings points to.

Usage: {$bash python jscribeit.py path/to/your/settings.json $}

Settings file is described here: {#settings}

@module jscribeit
"""

import argparse
import logging

from jscribe.utils.version import Version

from jscribe.core.docgenerator import DocumentationGenerator
from jscribe.conf import settings

logging.basicConfig(format='%(message)s', level=logging.INFO)

version = Version(0, 0, 2, 'a4')

parser = argparse.ArgumentParser(
    description='Generates documentation.'
)
parser.add_argument(
    'settings',
    type=str,
    help='Settings file path.',
)
args = parser.parse_args()

logging.info('JScribe documentation generator v{}.'.format(repr(version)))

generator = DocumentationGenerator(args.settings)
generator.generate_documentation()

logging.info('Documentation created in "{}".'.format(settings.DOCUMENTATION_OUTPUT_PATH))

# USAGE
"""* Usage, just run it in command line: {$bash python jscribeit.py path/to/your/settings.json $}

Settings file is described here: {#settings}

@manual usage "2. Usage"
"""

# DOCUMENTING CODE
"""* ##Documenting code.##

Documenting in JScribe is fairly easy.

###Guidelines###

What is documented is set explictly by user(You).

Your documentation must be contained between *doc string tags* and what is found there is called
*doc string*.

For javascript *doc string tags* are usually: opening `/**` and closing `*/`.
So example documention would look like this:

   ` /** Your documentation */ `

or multi line:

    /** Title
    Your documentation
    */


Nothing can preceed opening tag except whitespaces on its line, so this is wrong and won't be treated as documentation:

{$javascript var foo; /** This won't be documented*/ $}

String found in doc string before first *tag* in that doc string is treated as a description of
documented element (what is a tag and an element will be described later).

Indentation found before doc string opening tag will be treated as indentation for every line
in this doc string.
So text found in this doc string:

{$javascript
if (foo) {
    /** Title
        Indented Line:
    Your documentation
    */
}
$}

Will be this string:

     Title
        Indented Line:
    Your documentation

####Element tags####

**NOTICE** If you see `_` (underscore) before some char, in example: {{_#ref}}
    then this underscore has to be removed to work. I put it only because doc parser would parse it
    without it and You would not see it.

Tags are properties of doc string that says important things about element you are documenting.

Element is just a piece of code in your file, in example:

{$javascript
/**
!function foo
*/
var foo = function() {

}
$}

is documenting *function* element, where `!function` is a tag saying that this element is a function
with name foo. **NOTICE**. here I use `!` (exclamation mark) as a tag, but usually you would use `@`.

Doc string can contains **only** one element tag property.

What elements you can document is based on your *tag settings* (more about that {#tagsettings}).

Name of element is important, it has to be unique and can be referenced to other elements.
In example name `foo.bar` would mean that element name is *bar* and bar is a property of *foo* where
*foo* is also an element or is not defined at all.

You can reference to last defined element by preceding name with dot `.`:
{$javascript
/**
!function foo
*/
var foo = function() {
    /**
    !attribute .obj
    */
    this.obj = {
        /**
        !attribute ..name
        */
        name: 'bar'
    };
}
$}

In this example *obj* will be a property of *foo*. You can add more dots to indicate deeper level,
so *name* will be a child of *obj*.

Before tag there should be no other chars except whitespaces (but it depends on Your settings).

####Properties tags####

Take a look at this javascript code:

{$javascript
/** Module EntityFactory.
!module core.EntityFactory
!author xyz
*/
/** Keeps last created entity id.
!number .entity.currentEntityId
!private
*/
var currentEntityId = 0;
/** Entites are a containers for components.
!object .entity
!inherits {{Object}}
*/
var entityPrototype = {
    /** Initialize entity.
    !method .._init
    !param name {{str}} - Name of entity.
    */
    _init: function(name) {
        /** Id of entity.
        !number ..id
        !private
        */
        this.id = currentEntityId;
        currentEntityId += 1;
        this.name = name;
    }
};
/** Creates new entity.
!factory .EntityFactory
!return {{_#core.EntityFactory.entity}} - new entity
*/
var EntityFactory = function(name) {
    var newEntity = Object.create(entityPrototype);
    newEntity._init(name);
    return newEntity;
};
/** Prototype accessible from outside for inheritance.
!property ..entityPrototype
!valtype {{prototype}}
*/
EntityFactory.entityPrototype = entityPrototype;
$}

In this code there are few properties used:

- param, indicates parameter for element (should be used only on callable elements),
    between `{{ }}` you can pass type of value or reference to other element, like that:
    `{{_#absolute.path.to.element}}`. Syntax for param:
    `!param name([=default]|[...]) {{type}} - description`
- return, syntax: `!return {{type}} - description`, indicates what is returned from element on call
- valtype, syntax: `!valtype {{type}} - description` indicates type of this element value
- inherits, syntax: `!inherits {{type}}`, indicates from what this element inherits
- author, syntax `!author name`, just a name of an author of this script
- access, syntax: `!access public`, indicates way of access to that element in code
- private, it's a shortcut for `!access private`, there is also shortcut for public, constructor
    and static

####Inline tags####

Firstly you have to know that description are converted
using *markdown* markup, so you can use *markdown* in decriptions.

In descriptions you can also use inline tags.

Inline tags are:

- ref links, syntax: `{{_#absolute.path.to.element}}` - this will be
converted to link in documentation.
- code snippets, syntax:

    `{_$language code $}`

@manual documenting "4. Documenting code"
"""
