# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.recipe.script -- Tests suite
# :Creato:    sab 08 mar 2014 13:24:05 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import os
import sys
import unittest
import zc.buildout.tests
import zc.buildout.testing

from zope.testing import doctest, renormalizing

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('metapensiero.recipe.script', test)

    test.globs['os'] = os
    test.globs['sys'] = sys
    test.globs['test_dir'] = os.path.dirname(__file__)

def suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'tests.rst',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=optionflags,
            checker=renormalizing.RENormalizing([
                # If want to clean up the doctest output you
                # can register additional regexp normalizers
                # here. The format is a two-tuple with the RE
                # as the first item and the replacement as the
                # second item, e.g.
                # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                zc.buildout.testing.normalize_path,
            ]),
        ),
    ))

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
