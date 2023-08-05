# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys
import unittest
import argparse
from os.path import abspath, dirname, join as pjoin


def runtests(verbosity=1, failfast=True):
    here = abspath(dirname(__file__))
    root = pjoin(here, os.pardir, os.pardir)
    sys.path.insert(0, root)
    test_suite = unittest.defaultTestLoader.discover(here)
    runner = unittest.TextTestRunner(verbosity=verbosity, failfast=failfast)
    runner.run(test_suite)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Runs the test suite.'
        )
    parser.add_argument(
        '--failfast',
        dest='failfast',
        action='store_true',
        default=False,
        help='Stop running the test suite after first failed test.',
    )
    args = parser.parse_args()
    runtests(failfast=args.failfast)
