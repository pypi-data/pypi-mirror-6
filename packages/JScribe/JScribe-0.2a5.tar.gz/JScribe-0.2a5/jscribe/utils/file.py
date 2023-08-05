# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""* Module with common functions that help with file operations.
@module jscribe.utils.file
@author Rafał Łużyński
"""

import os
import re


def discover_files(input_paths, input_regex, ignore_paths_regex=[], ignore_regex=None):
    """* Return list of filepaths that align with given entry parameters
    (input paths, file regex, ignores).
    @function .discover_files
    @param input_paths {{list}} List of paths to directories that contains your files you want to be
    discovered.
    @param input_regex {{str}} regex that matches file names that should be discovered
    @param ignore_paths_regex=[] {{list}} list of regexes that match paths to directories that you
    want to exclude from your input_paths
    @param ignore_regex=None {{str}} regex that matches source file names that must not be discovered
    @return {{list}} - List of discovered filepaths
    """
    input_re = re.compile(input_regex)
    if ignore_regex is not None:
        ignore_re = re.compile(ignore_regex)
    # compile regex for ignore paths
    ignore_paths_regex_obj = []
    for path in ignore_paths_regex:
        ignore_paths_regex_obj.append(re.compile(path))
    file_paths = []
    for path in input_paths:
        for dirpath, dirnames, filenames in os.walk(path):
            if not _match_ignore_path(ignore_paths_regex_obj, dirpath):
                continue
            for filename in filenames:
                if ignore_regex is not None and ignore_re.match(filename):
                    continue
                if input_re.match(filename):
                    file_paths.append(os.path.join(dirpath, filename))
    return file_paths


def _match_ignore_path(ignore_paths_regex_obj, dirpath):
    for ignore_path_obj in ignore_paths_regex_obj:
        if ignore_path_obj.match(dirpath) is not None:
            return False
    return True


def get_py_file_encoding(path):
    """* Returns file encoding of python file.
    @function .get_py_file_encoding
    @param path {{str}} Path to py file.
    @return {{str}} encoding of py file
    """
    source_coding_re = re.compile(r'coding[:=]\s*(?P<coding>[-\w.]+)')
    source_coding = None
    with open(path, 'r') as f:
        # encoding must be on 1st or 2nd line in py file
        for i in range(2):
            match_inst = source_coding_re.search(f.readline())
            if match_inst is not None:
                source_coding = match_inst.group('coding')
                break
        f.close()
    return source_coding