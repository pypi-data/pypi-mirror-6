# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-mediaplayer utils """

import os
import tempfile
from shutil import rmtree
import unicodedata
import re

###########################################################
RE_NOTALPHANUM = re.compile('[^a-zA-Z0-9._\-]')

def wide_alpha_num(string):
    """Normalise a string to alpha numeric character

    "Â©" are replaced by "-c-"
    "&" are replaced by "_and_"

    other char except /[^a-zA-Z0-9._\-]/ are removed
    """
    string = string.replace(u'Â©', '-c-')
    # dump diacritical marks (Ã©,Ã ,Ã´,...)
    string = unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore')
    string = string.replace('&', '_and_')
    string = RE_NOTALPHANUM.sub('', string)
    return unicode(string)

def safe_hasattr(obj, attr):
    """return true if an obj have the given attribute (Safe hasattr

    Standard hasattr return false on **any** exception. This is a major defect.

    >>> class A(object):
    ...     toto=1
    ...     @property
    ...     def a(self):
    ...         raise RuntimeError('In soviet Russia Babar likes you!')
    ...
    >>> safe_hasattr(A(), 'toto')
    True
    >>> safe_hasattr(A(), 'tata')
    False
    >>> try:
    ...     safe_hasattr(A(), 'a')
    ... except RuntimeError, e:
    ...     print e
    ...
    In soviet Russia Babar likes you!
    """
    try:
        getattr(obj, attr)
        return True
    except AttributeError:
        return False

class TemporaryDir(object):
    """create a temporary directory on enter and remove it on exit

    this context is not reentrant"""

    def __init__(self, base=None, **kwargs):
        self._base = base
        self.root = None
        self.__kwargs = kwargs

    def __enter__(self):
        assert self.root is None
        self.root = tempfile.mkdtemp(prefix="temp-ctx-", dir=self._base, **self.__kwargs)
        return self

    def __exit__(self,  exctype, value, traceback):
        try:
            rmtree(self.root, ignore_errors=True)
        finally:
            self.root = None

    def sub(self):
        """Provide a TemporaryDir within this one"""
        assert self.root is not None
        return TemporaryDir(base=self.root)

    def filepath(self, **kwargs):
        """Provide a secure filename within this directory"""
        assert self.root is not None
        handler, path = tempfile.mkstemp(dir=self.root, **kwargs)
        os.close(handler)
        return path
