# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Builtin tag settings for python projects.

You can use them in project by setting TAG_SETTINGS to `jscribe.conf.pythontagsettings`, but
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
       "attributes": {}
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
        "list_order": 1,
        "attributes": {
        }
    },
    "module": {
        "parent_type": "base",
        "alias": [],
        "name": "module",
        "separate": True,
        "list_order": 2,
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
        "list_order": 0,
        "list": True,
        "attributes": {
        }
    },
    "exception": {
        "parent_type": "base",
        "name": "exception",
        "title": "Exceptions",
        "separate": False,
        "list_order": 0,
        "list": False,
        "attributes": {}
    },
    "method": {
        "parent_type": "base",
        "name": "method",
        "title": "methods",
        "callable": True,
        "separate": False,
        "attributes": {}
    },
    "property": {
        "parent_type": "base",
        "name": "property",
        "title": "properties",
        "callable": False,
        "separate": False,
        "attributes": {}
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
    "bytestring": {
        "parent_type": "attribute",
        "name": "bytestring",
        "alias": ["str"],
        "attributes": {
        }
    },
    "unicode": {
        "parent_type": "attribute",
        "name": "unicode",
        "alias": ["u"],
        "attributes": {
        }
    },
    "list": {
        "parent_type": "attribute",
        "name": "list",
        "alias": [],
        "attributes": {
        }
    },
    "tuple": {
        "parent_type": "attribute",
        "name": "tuple",
        "alias": [],
        "attributes": {}
    },
    "dict": {
        "parent_type": "attribute",
        "name": "dict",
        "alias": [],
        "attributes": {}
    },
}