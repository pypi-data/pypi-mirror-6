# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import FunctionalLayer, suite_from_package
from Products.Silva.testing import Browser

import unittest
import doctest

globs = {
    'grok': FunctionalLayer.grok,
    'getRootFolder': FunctionalLayer.get_application,
    'Browser': Browser,
    }

def create_test(build_test_suite, name):
    test =  build_test_suite(
        name,
        globs=globs,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
    test.layer = FunctionalLayer
    return test


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(suite_from_package(
            'silva.core.layout.tests.grok', create_test))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
