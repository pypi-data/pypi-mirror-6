# -*- coding: utf-8 -*-
#!/usr/bin/env python

import unittest

from jscribe.utils.version import Version


class TestVersion(unittest.TestCase):

    def setUp(self):
        self.versions_ok = [
            (0, 0, 1), (1, 2), (0, ), (112, 32532, 35), (1, 2, 3, 3, 4, 5), (0, 1, 2, 4, 'dev')
        ]
        self.versions_ok_repr = [
            '0.0.1', '1.2', '0', '112.32532.35', '1.2.3.3.4.5', '0.1.2.4dev'
        ]
        self.versions_wrong = [(), ('rb', 2), (12, 're', 312, '++'), (2, '', 1)]

    def test_version_init(self):
        for version in self.versions_ok:
            self.assertIsInstance(Version(*version), Version)
        for version in self.versions_wrong:
            self.assertRaises(ValueError, Version, *version)

    def test_repr(self):
        for index, version in enumerate(self.versions_ok):
            repre = self.versions_ok_repr[index]
            self.assertEqual(Version(*version).__repr__(), repre)
