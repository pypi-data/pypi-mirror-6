# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from zope.component import getMultiAdapter
from Products.Silva.testing import FunctionalLayer, TestRequest
from silva.core.layout.porto.interfaces import IPorto
from silva.core.interfaces import IPublicationWorkflow, IAccessSecurity


class PageTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('contact', u'Contact')
        IPublicationWorkflow(self.root.contact).publish()

    def test_public_rendering(self):
        """You can view public pages whenever you are authenticated or not.
        """
        browser = self.layer.get_browser()
        self.assertEqual(browser.open('http://localhost/root/contact'), 200)
        browser.login('viewer', 'viewer')
        self.assertEqual(browser.open('http://localhost/root/contact'), 200)

    def test_public_page(self):
        """You can query a page.
        """
        request = TestRequest(
            url='http://localhost/root/contact',
            layers=[IPorto])
        page = getMultiAdapter((self.root.contact, request), name='index.html')
        self.assertEqual(page.layout, None)
        self.assertNotEqual(page(), '')
        self.assertNotEqual(page.layout, None)

    def test_restricted_rendering(self):
        """You can only view restricted pages whenever you have the
        proper authentication.
        """
        IAccessSecurity(self.root.contact).minimum_role = 'Authenticated'

        browser = self.layer.get_browser()
        self.assertEqual(browser.open('http://localhost/root/contact'), 401)
        browser.login('viewer', 'viewer')
        self.assertEqual(browser.open('http://localhost/root/contact'), 200)

        IAccessSecurity(self.root.contact).minimum_role = 'Editor'

        self.assertEqual(browser.open('http://localhost/root/contact'), 401)
        browser.login('editor', 'editor')
        self.assertEqual(browser.open('http://localhost/root/contact'), 200)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PageTestCase))
    return suite
