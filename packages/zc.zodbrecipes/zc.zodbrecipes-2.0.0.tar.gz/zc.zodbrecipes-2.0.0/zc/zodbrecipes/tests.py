##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.testing import renormalizing

import doctest
import os
import pkg_resources
import re
import shutil
import sys
import tempfile
import unittest
import zc.buildout.testing
import zope.testing

try:
    from zc.buildout.testing import not_found
except ImportError:
    not_found = (re.compile(r'Not found: [^\n]+/(\w|\.)+/\r?\n'), '')

setuptools_or_distribute = (
    re.compile(r"[d-]  (setuptools|distribute)-"), "setuptools-")


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install('BTrees', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('ZEO', test)
    zc.buildout.testing.install('ZODB', test)
    zc.buildout.testing.install('persistent', test)
    zc.buildout.testing.install('six', test)
    zc.buildout.testing.install('transaction', test)
    zc.buildout.testing.install('zc.lockfile', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('zodbpickle', test)
    zc.buildout.testing.install('zope.event', test)
    zc.buildout.testing.install('zope.exceptions', test)
    zc.buildout.testing.install('zope.interface', test)
    zc.buildout.testing.install('zope.proxy', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install_develop('zc.zodbrecipes', test)


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    not_found,
    setuptools_or_distribute,
    ])

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'zeo.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            ),

        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
