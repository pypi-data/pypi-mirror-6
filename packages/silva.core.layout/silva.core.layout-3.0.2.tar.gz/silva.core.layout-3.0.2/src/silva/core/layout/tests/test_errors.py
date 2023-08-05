# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IAccessSecurity

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import FunctionalLayer


class ErrorPagesTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('document', 'Document')
        IAccessSecurity(self.root.folder.document).set_minimum_role('Viewer')

    def test_not_found(self):
        """Test default Silva not found page.
        """
        with self.layer.get_browser(public_settings) as browser:
            # Regular request
            self.assertEqual(
                browser.open('/root/folder/doesnotexist'),
                404)
            self.assertEqual(
                browser.headers['Content-Type'],
                'text/html;charset=utf-8')
            self.assertNotEqual(
                browser.contents,
                '')
            self.assertEqual(
                browser.inspect.title,
                ['404 Content not found'])
            # HEAD request
            self.assertEqual(
                browser.open('/root/folder/doesnotexist', method='HEAD'),
                404)
            self.assertEqual(
                browser.headers['Content-Length'],
                '0')
            self.assertEqual(
                browser.headers['Content-Type'],
                'text/html;charset=utf-8')
            self.assertEqual(
                browser.contents,
                '')

    def test_unauthorized(self):
        """test default Silva unauthorized page.
        """
        with self.layer.get_browser(public_settings) as browser:
            # Regular request
            self.assertEqual(
                browser.open('/root/folder/document'),
                401)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ErrorPagesTestCase))
    return suite
