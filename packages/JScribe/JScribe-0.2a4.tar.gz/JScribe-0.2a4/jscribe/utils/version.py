# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""*
@module jscribe.utils.version
@author Rafał Łużyński
"""

#TODO: write compare magic function
class Version(object):
    """* Just an auxillary class that represents version.
    @class .Version
    """

    def __init__(self, *args):
        self._is_version_valid(args)
        self._version = tuple(args)
        self._create_repr()

    def __repr__(self):
        return self._repr

    def _is_version_valid(self, version):
        if not version:
            raise ValueError('Version must have at least one number part')
        for i in version:
            if i != version[-1]:
                try:
                    int(i)
                except:
                    raise ValueError("Version parts must be an integer unless it's a last part.")

    def _create_repr(self):
        if type(self._version[-1]) == str:
            self._repr = u'.'.join(
                (unicode(i) for i in self._version[:-1])
            ) + unicode(self._version[-1])
        else:
            self._repr = u'.'.join((unicode(i) for i in self._version))
