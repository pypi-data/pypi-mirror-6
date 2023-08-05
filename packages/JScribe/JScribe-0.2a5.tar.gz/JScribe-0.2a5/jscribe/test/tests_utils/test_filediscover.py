# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import unittest
import shutil

from jscribe.utils.file import discover_files


class TestFileDiscover(unittest.TestCase):

    def setUp(self):
        """Create fir tree and files for discover test."""
        self.files_quantity_per_dir = 2
        self.dir_paths = ['1/1/1/', '1/2/1/', '1/2/2/', '2/1/1/1/', '1/', '2/1/', '2/', '1/ignore/']
        for dir_path in self.dir_paths:
            try:
                os.makedirs(dir_path)
            except:
                pass
            for i in range(1, self.files_quantity_per_dir + 1):
                with open(u'{}{}ąśęłó.test'.format(dir_path, str(i)), 'w') as f:
                    f.close()
                with open(u'{}{}ąśęłóignore.test'.format(dir_path, str(i)), 'w') as f:
                    f.close()

    def test_discover_files1(self):
        # discover files with one input path
        input_paths = [u'1/', ]
        input_regex = r'^.*?[.]test$'
        paths_to_find = set([
            u'1/1/1/1ąśęłó.test', u'1/1/1/2ąśęłó.test', u'1/2/1/1ąśęłó.test', u'1/2/1/2ąśęłó.test',
            u'1/2/2/1ąśęłó.test', u'1/2/2/2ąśęłó.test', u'1/1ąśęłó.test', u'1/2ąśęłó.test',
            u'1/ignore/1ąśęłó.test', u'1/ignore/2ąśęłó.test', u'1/1/1/1ąśęłóignore.test',
            u'1/1/1/2ąśęłóignore.test', u'1/2/1/1ąśęłóignore.test', u'1/2/1/2ąśęłóignore.test',
            u'1/2/2/1ąśęłóignore.test', u'1/2/2/2ąśęłóignore.test', u'1/1ąśęłóignore.test',
            u'1/2ąśęłóignore.test', u'1/ignore/1ąśęłóignore.test', u'1/ignore/2ąśęłóignore.test',
        ])
        found_paths = discover_files(input_paths, input_regex)
        self.assertEqual(set(found_paths), paths_to_find)

    def test_discover_files2(self):
        # discover files with two input paths
        input_paths = [u'1/', u'2/']
        input_regex = r'^.*?[.]test$'
        paths_to_find = set([
            u'1/1/1/1ąśęłó.test', u'1/1/1/2ąśęłó.test', u'1/2/1/1ąśęłó.test', u'1/2/1/2ąśęłó.test',
            u'1/2/2/1ąśęłó.test', u'1/2/2/2ąśęłó.test', u'2/1/1/1/1ąśęłó.test',
            u'2/1/1/1/2ąśęłó.test', u'1/1ąśęłó.test', u'1/2ąśęłó.test', u'2/1/1ąśęłó.test',
            u'2/1/2ąśęłó.test', u'2/1ąśęłó.test', u'2/2ąśęłó.test', u'1/ignore/1ąśęłó.test',
            u'1/ignore/2ąśęłó.test', u'1/1/1/1ąśęłóignore.test', u'1/1/1/2ąśęłóignore.test',
            u'1/2/1/1ąśęłóignore.test', u'1/2/1/2ąśęłóignore.test', u'1/2/2/1ąśęłóignore.test',
            u'1/2/2/2ąśęłóignore.test', u'2/1/1/1/1ąśęłóignore.test', u'2/1/1/1/2ąśęłóignore.test',
            u'1/1ąśęłóignore.test', u'1/2ąśęłóignore.test', u'2/1/1ąśęłóignore.test',
            u'2/1/2ąśęłóignore.test', u'2/1ąśęłóignore.test', u'2/2ąśęłóignore.test',
            u'1/ignore/1ąśęłóignore.test', u'1/ignore/2ąśęłóignore.test',
        ])
        found_paths = discover_files(input_paths, input_regex)
        self.assertEqual(set(found_paths), paths_to_find)

    def test_discover_files3(self):
        # discover files with two input paths and ignore path
        input_paths = [u'1/', u'2/']
        ignore_paths = [r'1/ignore.*?$']
        input_regex = r'^.*?[.]test$'
        paths_to_find = set([
            u'1/1/1/1ąśęłó.test', u'1/1/1/2ąśęłó.test', u'1/2/1/1ąśęłó.test', u'1/2/1/2ąśęłó.test',
            u'1/2/2/1ąśęłó.test', u'1/2/2/2ąśęłó.test', u'2/1/1/1/1ąśęłó.test',
            u'2/1/1/1/2ąśęłó.test', u'1/1ąśęłó.test', u'1/2ąśęłó.test', u'2/1/1ąśęłó.test',
            u'2/1/2ąśęłó.test', u'2/1ąśęłó.test', u'2/2ąśęłó.test', u'1/1/1/1ąśęłóignore.test',
            u'1/1/1/2ąśęłóignore.test', u'1/2/1/1ąśęłóignore.test', u'1/2/1/2ąśęłóignore.test',
            u'1/2/2/1ąśęłóignore.test', u'1/2/2/2ąśęłóignore.test', u'2/1/1/1/1ąśęłóignore.test',
            u'2/1/1/1/2ąśęłóignore.test', u'1/1ąśęłóignore.test', u'1/2ąśęłóignore.test',
            u'2/1/1ąśęłóignore.test', u'2/1/2ąśęłóignore.test', u'2/1ąśęłóignore.test',
            u'2/2ąśęłóignore.test',
        ])
        found_paths = discover_files(input_paths, input_regex, ignore_paths_regex=ignore_paths)
        self.assertEqual(set(found_paths), paths_to_find)

    def test_discover_files4(self):
        # discover files with two input paths, ignore path and ignore regex
        input_paths = [u'1/', u'2/']
        ignore_paths = [r'1/ignore.*?$']
        input_regex = r'^.*?[.]test$'
        ignore_regex = r'^.*?ignore[.]test$'
        paths_to_find = set([
            u'1/1/1/1ąśęłó.test', u'1/1/1/2ąśęłó.test', u'1/2/1/1ąśęłó.test', u'1/2/1/2ąśęłó.test',
            u'1/2/2/1ąśęłó.test', u'1/2/2/2ąśęłó.test', u'2/1/1/1/1ąśęłó.test',
            u'2/1/1/1/2ąśęłó.test', u'1/1ąśęłó.test', u'1/2ąśęłó.test', u'2/1/1ąśęłó.test',
            u'2/1/2ąśęłó.test', u'2/1ąśęłó.test', u'2/2ąśęłó.test',
        ])
        found_paths = discover_files(
            input_paths, input_regex, ignore_paths_regex=ignore_paths, ignore_regex=ignore_regex
        )
        self.assertEqual(set(found_paths), paths_to_find)

    def test_discover_files5(self):
        # discover files with two input paths, ignore path and ignore regex, second input regex
        input_paths = [u'1/', u'2/']
        ignore_paths = [r'1/ignore.*?$']
        input_regex = r'^2.*?[.]test$'
        ignore_regex = r'^.*?ignore[.]test$'
        paths_to_find = set([
            u'1/1/1/2ąśęłó.test', u'1/2/1/2ąśęłó.test', u'1/2/2/2ąśęłó.test',
            u'2/1/1/1/2ąśęłó.test', u'1/2ąśęłó.test', u'2/1/2ąśęłó.test', u'2/2ąśęłó.test',
        ])
        found_paths = discover_files(
            input_paths, input_regex, ignore_paths_regex=ignore_paths, ignore_regex=ignore_regex
        )
        self.assertEqual(set(found_paths), paths_to_find)

    def tearDown(self):
        """Remove test dir tree and files."""
        for dir_path in self.dir_paths:
            try:
                shutil.rmtree(dir_path)
            except OSError:
                pass
