# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import json
import codecs
import unittest
import textwrap
from collections import OrderedDict

from jscribe.utils.file import get_source_file_coding
from jscribe.core.docstringparser import DocStringParser


class TestDocStringParser(unittest.TestCase):

    def setUp(self):
        """Create test files to parse."""
        with open('testtagsettings.json', 'w') as f:
            json.dump({
                'default': {
                   'parent_type': None,
                   'alias': [],
                   'separate': False,
                   'name': 'default name',
                   'title': 'default plural name',
                   'callable': False,
                   'attributes': {
                       'access': 'public',
                       'example': None,
                       'params': [],
                       'return': None,
                       'inherits': None,
                       'default': None,
                       'valtype': None,
                       'author': None,
                       'license': None,
                       'version': None,
                   }
                },
                'package': {
                    'parent_type': 'default',
                    'alias': ['pack'],
                    'name': 'package',
                    'title': 'packages',
                    'separate': True,
                    'callable': True,
                    'attributes': {
                    }
                },
                'file': {
                    'parent_type': 'default',
                    'alias': [],
                    'name': 'file',
                    'separate': True,
                    'title': 'files',
                    'callable': True,
                    'attributes': {
                    }
                },
                'factory': {
                    'parent_type': 'default',
                    'name': 'factory',
                    'title': 'factories',
                    'callable': True,
                    'attributes': {
                        'return': {
                            'type': 'Object',
                            'description': None
                        }
                    }
                },
                'method': {
                    'parent_type': 'default',
                    'name': 'method',
                    'title': 'methods',
                    'callable': True,
                    'attributes': {
                        'return': {
                            'type': None,
                            'description': None
                        }
                    }
                },
                'function': {
                    'parent_type': 'default',
                    'name': 'function',
                    'title': 'functions',
                    'callable': True,
                    'attributes': {
                        'return': {
                            'type': None,
                            'description': None
                        }
                    }
                },
                'object': {
                    'parent_type': 'default',
                    'name': 'object',
                    'title': 'objects',
                    'callable': False,
                    'attributes': {
                    }
                },
                'property': {
                    'parent_type': 'default',
                    'name': 'property',
                    'title': 'properties',
                    'callable': False,
                    'attributes': {
                    }
                },
                'number': {
                    'parent_type': 'property',
                    'alias': ['num'],
                    'attributes': {
                        'valtype': 'number'
                    }
                },
                'string': {
                    'parent_type': 'property',
                    'alias': ['str'],
                    'attributes': {
                        'valtype': 'string'
                    }
                },
            }, f)
            f.close()
        with open('testtagsettings.json', 'r') as f:
            self.tag_settings = json.load(f)
            f.close()
        self.doc_string_regex = (r'[/][*][*]', r'[*][/]')
        self.tag_regex = r'[@](?P<tag>.*?)\s'
        self.new_line_replace = '<br/>'
        with open('testdocfile1.js', 'w') as f:
            f.write("""\
                /** File defines EntityFactory module.
                @file core.EntityFactory
                @author Rafał Łużyński
                */
                define(function() {
                    /** Keeps last created entity id.
                    @number .EntityFactory.currentEntityId
                    @private
                    */
                    var currentEntityId = 0;
                    /** Entites are a containers for components.
                    @object .entity
                    @inherits {{Object}}
                    */
                    var entityPrototype = {
                        /** Initialize entity.
                        @method .._init
                        */
                        _init: function() {
                            /** Id of entity.
                            @number ..id
                            */
                            this.id = currentEntityId;
                            currentEntityId += 1;
                        }
                    };
                    /** Creates new entity.
                    @factory .EntityFactory
                    @return {{core.EntityFactory.entity}} New entity.
                    @example example1 {$var EntityFactory = require('core/EntityFactory');
                    var entity = EntityFactory();$}
                    */
                    var EntityFactory = function() {
                        var newEntity = Object.create(entityPrototype);
                        newEntity._init();
                        return newEntity;
                    };
// comment          /** this is not a doc string
                    @number
                    */
                    /** this is not a doc string neither, because of no tag
                    */
                    /** Prototype accessible from outside for inheritance.
                    @property ..entityPrototype
                    @valtype {{prototype}}
                    */
                    EntityFactory.entityPrototype = entityPrototype;
                    return EntityFactory;
                });
            """)
            f.close()
        with open('testdocfile2.js', 'w') as f:
            f.write("""\
                /**
                File defines ComponentFactory module.
                @file core.ComponentFactory
                @author Rafał Łużyński
                */
                define(function() {
                    /**
                    Components are properties of entities.
                    Test url: [Test](http://test.com).
                    @object .component
                    @inherits {{Object}}
                    */
                    var componentPrototype = {
                        /**
                        Initialize component.
                        @method .._init
                        */
                        _init: function() {
                            /** Name of component.
                            @string ..name
                            */
                            name: undefined
                        }
                    };
                    /**
                    Creates new component.
                    @factory .ComponentFactory
                    @return {{core.ComponentFactory.component}} New component.
                    @example example1 {$var ComponentFactory = require('core/ComponentFactory');
                    var component = ComponentFactory();$}
                    */
                    var ComponentFactory = function() {
                        var newComponent = Object.create(componentPrototype);
                        newComponent._init();
                        return newComponent;
                    };
                    /**
                    Prototype accessible from outside for inheritance.
                    @property ..componentPrototype
                    @valtype {{prototype}}
                    */
                    ComponentFactory.componentPrototype = componentPrototype;
                    return ComponentFactory;
                });
            """)
            f.close()
        with codecs.open('testdocfile3.js', 'w', 'utf-8') as f:
            f.write(u"""\
                /**
                File defines VelocityComponentFactory module.
                @file core.VelocityComponentFactory
                @author Rafał Łużyński
                */
                define(function() {
                    /**
                    Velocity is needed for movement of entites.
                    Based on [Component](#core.ComponentFactory.component "Component").
                    @object .velocity
                    @inherits {{core.ComponentFactory.component}}
                    */
                    return VelocityComponentFactory;
          //comment /** this is not a doc string because of comment @number */
                });
            """)
            f.close()
        with open('testdocfilepackage.js', 'w') as f:
            f.write("""\
                /** Core files package.
                @pack core
                @author Rafał Łużyński
                */
            """)
            f.close()
        with open('testdocfile4.js', 'w') as f:
            f.write("""\
                /**
                File defines Error module.
                @file
                */
            """)
            f.close()
        with open('testdocfile5.js', 'w') as f:
            f.write("""\
                /** Default author test.
                @file author
                @author
                */
            """)
            f.close()
        with open('testdocfile6.js', 'w') as f:
            f.write("""\
                /**
                No object name.
                @file noobjectname
                @author RŁ
                */
                /**
                Object error.
                @object
                */
            """)
            f.close()
        with open('testdocfile8.js', 'w') as f:
            f.write("""\
                /**
                 Invalid block tag.
                 @file test
                 @author RŁ
                */
                /**
                 Object error.
                 @object .test1
                 @function .test2
                */
            """)
            f.close()

        with open('testdocfile9.js', 'w') as f:
            f.write("""\
                /**
                 Invalid tag.
                 @file test
                 @foobar invalidtag
                 @author RŁ
                */
            """)
            f.close()

        with open('testdocfile10.js', 'w') as f:
            f.write("""\
                /**
                 Invalid path.
                 @object foo..bar
                 @author RŁ
                */
            """)
            f.close()

        with open('testdocfile11.js', 'w') as f:
            f.write("""\
                /**
                 Invalid path 2.
                 @object foo.bar.
                 @author RŁ
                */
            """)
            f.close()
        with codecs.open('testdocfileinvalidutf8.js', 'w', 'utf-8') as f:
            f.write(u"""\
                #!/usr/bin/env python
                # -*- coding: utf-16 -*-
                /**
                 Invalid encoding.
                 @object foo
                 @author Rafał Łużyński
                */
            """)
            f.close()

    def test_doc_string_parser_file_1(self):
        """Test if data parsing and collecting works as expected."""
        data = OrderedDict({
            'properties': OrderedDict({
                'core': {
                    'properties': OrderedDict({
                        'EntityFactory': {
                            'filepath': 'testdocfile1.js',
                            'properties': OrderedDict({
                                'EntityFactory': {
                                    'properties': OrderedDict({
                                        'currentEntityId': {
                                            'properties': OrderedDict({}),
                                            'name': 'currentEntityId',
                                            'alias_name': None,
                                            'type': 'number',
                                            'description': 'Keeps last created entity id.',
                                            'attributes': {
                                                'access': 'private',
                                            },
                                            'startline': 6,
                                            'endline': 9,
                                            'filepath': 'testdocfile1.js',
                                        },
                                        'entityPrototype': {
                                            'name': 'entityPrototype',
                                            'alias_name': None,
                                            'properties': OrderedDict({}),
                                            'type': 'property',
                                            'description': textwrap.dedent("""
                                                Prototype accessible from outside for inheritance.
                                            """).strip('\n'),
                                            'startline': 43,
                                            'endline': 46,
                                            'attributes': {
                                                'valtype': {
                                                    'valtype': 'prototype',
                                                    'ref': None,
                                                    'default': None,
                                                    'description': ''
                                                }
                                            },
                                            'filepath': 'testdocfile1.js',
                                        },
                                    }),
                                    'filepath': 'testdocfile1.js',
                                    'type': 'factory',
                                    'name': 'EntityFactory',
                                    'alias_name': None,
                                    'description': 'Creates new entity.',
                                    'startline': 27,
                                    'endline': 32,
                                    'attributes': {
                                        'return': {
                                            'type': {
                                                'type': 'core.EntityFactory.entity',
                                                'ref': None,
                                            },
                                            'description': 'New entity.',
                                        },
                                        'examples': [
                                            {
                                                'code': textwrap.dedent("""\
                                                var EntityFactory = require('core/EntityFactory');
                                                var entity = EntityFactory();
                                                """).strip('\n'),
                                                'title': 'example1',
                                                'langid': None,
                                                'description': '',
                                            }
                                        ]
                                    },
                                },
                                'entity': {
                                    'properties': OrderedDict({
                                        '_init': {
                                            'properties': OrderedDict({}),
                                            'type': 'method',
                                            'description': 'Initialize entity.',
                                            'startline': 16,
                                            'endline': 18,
                                            'name': '_init',
                                            'alias_name': None,
                                            'filepath': 'testdocfile1.js',
                                            'attributes': {},
                                        },
                                        'id': {
                                            'properties': OrderedDict({}),
                                            'type': 'number',
                                            'description': 'Id of entity.',
                                            'startline': 20,
                                            'endline': 22,
                                            'name': 'id',
                                            'alias_name': None,
                                            'filepath': 'testdocfile1.js',
                                            'attributes': {},
                                        }
                                    }),
                                    'filepath': 'testdocfile1.js',
                                    'type': 'object',
                                    'description': 'Entites are a containers for components.',
                                    'startline': 11,
                                    'endline': 14,
                                    'name': 'entity',
                                    'alias_name': None,
                                    'attributes': {
                                        'inherits': {
                                            'inherits': 'Object',
                                            'ref': None,
                                        }
                                    },
                                }
                            }),
                            'description': 'File defines EntityFactory module.',
                            'attributes': {
                                'author': 'Rafał Łużyński',
                            },
                            'startline': 1,
                            'endline': 4,
                            'name': 'EntityFactory',
                            'alias_name': None,
                            'type': 'file',
                        },
                    }),
                    'filepath': 'testdocfilepackage.js',
                    'attributes': {
                        'author': 'Rafał Łużyński',
                    },
                    'startline': 1,
                    'endline': 4,
                    'name': 'core',
                    'alias_name': None,
                    'type': 'package',
                    'description': 'Core files package.',
                },
            }),
        })
        self.maxDiff = None
        filepaths = ['testdocfilepackage.js', 'testdocfile1.js']
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        for filepath in filepaths:
            dsp.parse_file(filepath)
        self.assertEqual(
            dsp.data['properties']['core']
                    ['properties']['EntityFactory']
                    ['properties']['EntityFactory']
                    ['properties'],
            data['properties']['core']
                ['properties']['EntityFactory']
                ['properties']['EntityFactory']
                ['properties']
        )
        self.assertEqual(
            dsp.data,
            data
        )

    def test_doc_string_parser_file_2(self):
        """Test if data parsing and collecting works as expected."""
        data = OrderedDict({
            'properties': OrderedDict({
                'core': {
                    'properties': OrderedDict({
                        'ComponentFactory': {
                            'filepath': 'testdocfile2.js',
                            'properties': OrderedDict([
                                ('component', {
                                    'properties': OrderedDict({
                                        '_init': {
                                            'properties': OrderedDict({}),
                                            'type': 'method',
                                            'description': 'Initialize component.',
                                            'startline': 14,
                                            'endline': 17,
                                            'filepath': 'testdocfile2.js',
                                            'name': '_init',
                                            'alias_name': None,
                                            'attributes': {},
                                        },
                                        'name': {
                                            'properties': OrderedDict({}),
                                            'type': 'string',
                                            'description': 'Name of component.',
                                            'startline': 19,
                                            'endline': 21,
                                            'filepath': 'testdocfile2.js',
                                            'name': 'name',
                                            'alias_name': None,
                                            'attributes': {},
                                        }
                                    }),
                                    'name': 'component',
                                    'alias_name': None,
                                    'type': 'object',
                                    'description': textwrap.dedent("""\
                                        Components are properties of entities.
                                        Test url: [Test](http://test.com).
                                    """).strip('\n'),
                                    'startline': 7,
                                    'endline': 12,
                                    'attributes': {
                                        'inherits': {
                                            'inherits': 'Object',
                                            'ref': None,
                                        }
                                    },
                                    'filepath': 'testdocfile2.js',
                                }),
                                ('ComponentFactory', {
                                    'properties': OrderedDict({
                                        'componentPrototype': {
                                            'properties': OrderedDict({}),
                                            'type': 'property',
                                            'description': textwrap.dedent("""\
                                                Prototype accessible from outside for inheritance.
                                            """).strip('\n'),
                                            'startline': 37,
                                            'endline': 41,
                                            'attributes': {
                                                'valtype': {
                                                    'valtype': 'prototype',
                                                    'ref': None,
                                                    'description': '',
                                                    'default': None
                                                }
                                            },
                                            'filepath': 'testdocfile2.js',
                                            'name': 'componentPrototype',
                                            'alias_name': None,
                                        },
                                    }),
                                    'name': 'ComponentFactory',
                                    'alias_name': None,
                                    'type': 'factory',
                                    'description': 'Creates new component.',
                                    'filepath': 'testdocfile2.js',
                                    'startline': 25,
                                    'endline': 31,
                                    'attributes': {
                                        'return': {
                                            'type': {
                                                'type': 'core.ComponentFactory.component',
                                                'ref': None,
                                            },
                                            'description': 'New component.',
                                        },
                                        'examples': [
                                            {
                                                'code': textwrap.dedent("""\
                                            var ComponentFactory = require('core/ComponentFactory');
                                            var component = ComponentFactory();
                                                """).strip('\n'),
                                                'description': '',
                                                'title': 'example1',
                                                'langid': None,
                                            }
                                        ]
                                    }
                                }),
                            ]),
                            'description': 'File defines ComponentFactory module.',
                            'attributes': {
                                'author': 'Rafał Łużyński',
                            },
                            'startline': 1,
                            'endline': 5,
                            'name': 'ComponentFactory',
                            'alias_name': None,
                            'type': 'file',
                        },
                    }),
                    'filepath': 'testdocfilepackage.js',
                    'attributes': {
                        'author': 'Rafał Łużyński',
                    },
                    'startline': 1,
                    'endline': 4,
                    'name': 'core',
                    'alias_name': None,
                    'type': 'package',
                    'description': 'Core files package.',
                },
            })
        })
        filepaths = ['testdocfilepackage.js', 'testdocfile2.js']
        self.maxDiff = None
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        for filepath in filepaths:
            dsp.parse_file(filepath)
        self.assertEqual(dsp.data, data)

    def test_doc_string_parser_file_3(self):
        """Test if data parsing and collecting works as expected."""
        data = OrderedDict({
            'properties': OrderedDict({
                'core': {
                    'properties': OrderedDict({
                        'VelocityComponentFactory': {
                            'filepath': 'testdocfile3.js',
                            'properties': OrderedDict({
                                'velocity': {
                                    'properties': OrderedDict({}),
                                    'type': 'object',
                                    'description': textwrap.dedent("""\
                                Velocity is needed for movement of entites.
                                Based on [Component](#core.ComponentFactory.component "Component").
                                    """).strip('\n'),
                                    'startline': 7,
                                    'endline': 12,
                                    'attributes': {
                                        'inherits': {
                                            'inherits': 'core.ComponentFactory.component',
                                            'ref': None,
                                        }
                                    },
                                    'filepath': 'testdocfile3.js',
                                    'name': 'velocity',
                                    'alias_name': None,
                                }
                            }),
                            'description': 'File defines VelocityComponentFactory module.',
                            'attributes': { 'author': 'Rafał Łużyński', },
                            'startline': 1,
                            'endline': 5,
                            'name': 'VelocityComponentFactory',
                            'alias_name': None,
                            'type': 'file',
                        },
                    }),
                    'filepath': 'testdocfilepackage.js',
                    'attributes': { 'author': 'Rafał Łużyński', },
                    'startline': 1,
                    'endline': 4,
                    'name': 'core',
                    'alias_name': None,
                    'type': 'package',
                    'description': 'Core files package.',
                },
            }),
        })
        filepaths = [
            'testdocfilepackage.js', 'testdocfile3.js'
        ]
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        self.maxDiff = None
        for filepath in filepaths:
            dsp.parse_file(filepath)
        self.assertEqual(dsp.data, data)

    def test_doc_string_parser_no_file_name(self):
        """Raise error if no file name is provided."""
        filepath = 'testdocfile4.js'
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        self.assertRaises(DocStringParser.TagValueException, dsp.parse_file, filepath)

    def test_doc_string_parser_no_tag_name(self):
        """Raise error if no tag name value is provided."""
        filepath = 'testdocfile6.js'
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        self.assertRaises(DocStringParser.TagValueException, dsp.parse_file, filepath)

    def test_doc_string_parser_invalid_doc_string(self):
        """Raise error if no two block tags are given in one doc string."""
        filepath = 'testdocfile8.js'
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        self.assertRaises(DocStringParser.InvalidDocStringException, dsp.parse_file, filepath)

    def test_doc_string_parser_invalid_path_element(self):
        """Raise error if no two block tags are given in one doc string."""
        filepath = 'testdocfile10.js'
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        self.assertRaises(DocStringParser.InvalidElementPathException, dsp.parse_file, filepath)

    def test_doc_string_parser_invalid_path_element2(self):
        """Raise error if no two block tags are given in one doc string."""
        filepath = 'testdocfile11.js'
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        self.assertRaises(DocStringParser.InvalidElementPathException, dsp.parse_file, filepath)

    def test_doc_string_parser_invalid_tag(self):
        """Raise error if doc string contains invalid tag if config property is set to False."""
        filepath = 'testdocfile9.js'
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        self.assertRaises(DocStringParser.InvalidTagException, dsp.parse_file, filepath)
        dsp.ignore_invalid_tags = True
        try:
            dsp.parse_file(filepath)
        except DocStringParser.InvalidTagException:
            self.fail('InvalidTagException raised')

    def test_doc_string_parser_default_author(self):
        """Test if data parsing and collecting works as expected with one file."""
        data = OrderedDict({
            'properties': OrderedDict({
                'author': {
                    'filepath': 'testdocfile5.js',
                    'properties': OrderedDict({}),
                    'description': 'Default author test.',
                    'attributes': { 'author': '', },
                    'startline': 1,
                    'endline': 4,
                    'name': 'author',
                    'alias_name': None,
                    'type': 'file',
                },
            }),
        })
        filepaths = ['testdocfile5.js']
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        for filepath in filepaths:
            dsp.parse_file(filepath)
        self.assertEqual(dsp.data, data)

    def test_get_doc_strings(self):
        """Test finding doc strings in a file."""
        dsp = DocStringParser(
            self.tag_settings, self.doc_string_regex, self.tag_regex
        )
        doc_strings = dsp._get_doc_strings('testdocfile3.js', 'utf-8')
        doc_strings_check = [
            (1, 5, textwrap.dedent(u"""
                File defines VelocityComponentFactory module.
                @file core.VelocityComponentFactory
                @author Rafał Łużyński
            """)),
            (7, 12, textwrap.dedent("""
                Velocity is needed for movement of entites.
                Based on [Component](#core.ComponentFactory.component "Component").
                @object .velocity
                @inherits {{core.ComponentFactory.component}}
            """))
        ]
        self.assertEqual(doc_strings, doc_strings_check)

    def test_invalid_coding_in_source_file(self):
        """Raise error if encoding of file is invalid."""
        filepath = 'testdocfileinvalidutf8.js'
        dsp = DocStringParser(self.tag_settings, self.doc_string_regex, self.tag_regex)
        self.assertEqual(get_source_file_coding(filepath), 'utf-16')
        self.assertRaises(UnicodeError, dsp.parse_file, filepath)

    def tearDown(self):
        os.remove('testdocfilepackage.js')
        os.remove('testdocfile1.js')
        os.remove('testdocfile2.js')
        os.remove('testdocfile3.js')
        os.remove('testdocfile4.js')
        os.remove('testdocfile5.js')
        os.remove('testdocfile6.js')
        os.remove('testdocfile8.js')
        os.remove('testdocfile9.js')
        os.remove('testdocfile10.js')
        os.remove('testdocfile11.js')
        os.remove('testdocfileinvalidutf8.js')
        os.remove('testtagsettings.json')
