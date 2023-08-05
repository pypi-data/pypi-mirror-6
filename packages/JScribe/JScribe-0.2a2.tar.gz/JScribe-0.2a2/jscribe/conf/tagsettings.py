# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Default tag settings **for overwrite**
@module jscribe.conf.tagsettings
"""

TAG_SETTINGS = {
    "base": {
       "parent_type": None,
       "alias": [],
       "separate": False,
       "list": False,
       "list_order": 0,
       "name": "default name",
       "title": "default plural name",
       "source_visible": True,
       "callable": False,
       "attributes": {
           "access": "public",
           "valtype": None,
       }
    },
}


# TAGSETTINGS MANUAL

"""* *tagsettings* is a file where can customize your documentation elements.

Lets say that you are creating entity based game engine. In such engine exists three basic elements:

- entites,
- components,
- systems.

Usually you create lot of classes/objects that inherits from these three.

Now to easly indicate in documentation that this object is an entity, and not just a class,
factory or object you can create new tag *entity* in this file.
To create new entity element in documentation you just input `@entity big_monster` instead of
`@class big_monster`. By labeling your doc elements like that you get another features, in example
JScribe can create list of all entites for you in menu. You can also create different templates for
different tags, this will be described in templates section.

Your own tagsettings file has to be in json format.

Example tagsettings file:

{$json
{
    "base": {
        "parent_type": null,
        "alias": [],
        "separate": false,
        "list": false,
        "list_order": 0,
        "name": "default name",
        "title": "default plural name",
        "source_visible": true,
        "callable": false,
        "attributes": {}
    },
    "class": {
        "parent_type": "base",
        "alias": ["cls"],
        "separate": true,
        "list": true,
        "list_order": 0,
        "name": "class",
        "title": "Classes",
        "source_visible": true,
        "callable": false,
        "attributes": {}
    },
    "function": {
        "parent_type": "base",
        "alias": ["func"],
        "separate": false,
        "list": false,
        "list_order": 0,
        "name": "function",
        "title": "Functions",
        "source_visible": true,
        "callable": true,
        "attributes": {}
    },
    "entity": {
        "parent_type": "base",
        "alias": ["ent"],
        "separate": true,
        "list": true,
        "list_order": 0,
        "name": "entity",
        "title": "Entities",
        "source_visible": true,
        "callable": false,
        "attributes": {}
    }
}
$}

As you can see tag have few properties that you can set.

####Properties:####

- **parent_type**: this is name of tag that this tag will inherit from, in example if
    some property `foo` won't be found in current tag, then it will be taken from parent tag
- **alias**: this is an array of alias names for tag, so instead of `@class` you can use `@cls`
- **separate**: if this is true then new file will be created for every element of this tag, if
    this element is a child of another element, then it won't be placed under this child in doc, but
    instead there will be link pointing to file with documentation for this element.
- **list**: if this is true then list of this tag elements will be created in template
- **list_order**: by this value lists are ordered in template view, lesser value means higher
    position
- **name**: name of this tag, that will be shown in documentation
- **title**: title of list of elements of this tag
- **source_visisble**: if true, then link to source file documentation will be placed in doc
- **callable**: if true, then it means that this code element can be called, in template it will be
    indicated with parenteshis after element name
- **attributes**: these are used internally in program only for now

You can also use builtin tagsettings, these are: `jscribe.conf.pythontagsettings` and
    `jscribe.conf.jstagsettings`

@manual tagsettings "5. Tag settings"
"""