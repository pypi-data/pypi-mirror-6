# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Builtin tag settings for javascript projects.

You can use them in project by setting TAG_SETTINGS to `jscribe.conf.jstagsettings`, but
I admit you to create your own tag settings.
@module jscribe.conf.jstagsettings
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
       }
    },
    "index": {
        "parent_type": "base",
        "alias": ["a"],
        "name": "",
        "title": "Index",
        "separate": True,
        "source_visible": True,
        "list": True,
        "list_order": -2,
        "attributes": {
        }
    },
    "manual": {
        "parent_type": "base",
        "alias": ["m"],
        "name": "",
        "title": "Manual",
        "separate": True,
        "source_visible": True,
        "list": True,
        "list_order": -1,
        "attributes": {
        }
    },
    "paragraph": {
        "parent_type": "base",
        "alias": ["p"],
        "name": "",
        "title": "paragraphs",
        "separate": False,
        "source_visible": True,
        "list": False,
        "attributes": {
        }
    },
    "package": {
        "parent_type": "base",
        "alias": ["pack"],
        "name": "package",
        "title": "API Packages",
        "separate": True,
        "list": True,
        "attributes": {
        }
    },
    "module": {
        "parent_type": "base",
        "alias": [],
        "name": "module",
        "separate": True,
        "list": True,
        "title": "API Modules",
        "attributes": {
        }
    },
    "class": {
        "parent_type": "base",
        "name": "class",
        "title": "API Classes",
        "separate": False,
        "list": True,
        "attributes": {
        }
    },
    "method": {
        "parent_type": "base",
        "name": "method",
        "title": "methods",
        "callable": True,
        "separate": False,
        "attributes": {
        }
    },
    "instance": {
        "parent_type": "base",
        "name": "instance",
        "title": "instances",
        "separate": False,
        "attributes": {
        }
    },
    "function": {
        "parent_type": "base",
        "name": "function",
        "title": "functions",
        "callable": True,
        "attributes": {
        }
    },
    "attribute": {
        "parent_type": "base",
        "alias": ["attr"],
        "name": "attribute",
        "title": "attributes",
        "callable": False,
        "attributes": {
        }
    },
    "number": {
        "parent_type": "attribute",
        "name": "number",
        "alias": ["num"],
        "attributes": {
        }
    },
    "string": {
        "parent_type": "attribute",
        "name": "string",
        "alias": ["str"],
        "attributes": {
        }
    },
    "array": {
        "parent_type": "base",
        "name": "array",
        "alias": [],
        "attributes": {
        }
    },
    "object": {
        "parent_type": "base",
        "name": "object",
        "alias": [],
        "attributes": {
        }
    },
}