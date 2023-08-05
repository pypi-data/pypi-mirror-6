# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.ftesting import public_settings
from Products.Silva.testing import FunctionalLayer
from silva.core.interfaces import IPublicationWorkflow, IAccessSecurity


class ContainerNavigationTestCase(unittest.TestCase):
    """Test container navigation links. A container should appear if
    it as a published index and it is not hidden from the tocs.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('about', u'About')
        factory.manage_addFolder('support', 'Support')
        factory.manage_addFolder('documentation', 'Documentation')
        factory.manage_addFolder('contact', 'Contact')
        factory = self.root.support.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('index', u'Contact')
        factory = self.root.documentation.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('index', u'Documentation')
        IPublicationWorkflow(self.root.support.index).publish()
        IPublicationWorkflow(self.root.about).publish()

        self.layer.logout()

    def test_public(self):
        browser = self.layer.get_browser(public_settings)

        self.assertEqual(browser.open('http://localhost/root'), 200)
        self.assertEqual(browser.location, '/root')

        self.assertEqual(
            browser.inspect.navigation,
            [u'About', u'Support'])
        link = browser.inspect.navigation['about']
        self.assertEqual(link.url, 'http://localhost/root/about')
        link = browser.inspect.navigation['Support']
        self.assertEqual(link.url, 'http://localhost/root/support')

    def test_preview(self):
        browser = self.layer.get_browser(public_settings)

        self.assertEqual(browser.open('http://localhost/root/++preview++'), 401)

        # Author should be able to acess
        browser.login('author', 'author')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 200)
        self.assertEqual(browser.location, '/root/++preview++')

        self.assertEqual(
            browser.inspect.navigation,
            [u'About', u'Support', u'Documentation'])
        link = browser.inspect.navigation['about']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/about')
        link = browser.inspect.navigation['Support']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/support')
        link = browser.inspect.navigation['Documentation']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/documentation')


class ContentNavigationTestCase(unittest.TestCase):
    """Test content navigation links. A content should appear, if it
    is published, not hidden from the tocs, and the minimum roles
    match the one of the visitor.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('info', u'Information')
        factory.manage_addMockupVersionedContent('contact', u'Contact')
        factory.manage_addMockupVersionedContent('product', u'Product')
        factory.manage_addMockupVersionedContent('specs', u'Specs')
        IPublicationWorkflow(self.root.info).publish()
        IPublicationWorkflow(self.root.product).publish()
        IAccessSecurity(self.root.product).minimum_role = 'Viewer'
        IAccessSecurity(self.root.specs).minimum_role = 'Editor'

        self.layer.logout()

    def test_public(self):
        """In public, you see the links that are public.
        """
        browser = self.layer.get_browser(public_settings)

        self.assertEqual(browser.open('http://localhost/root'), 200)
        self.assertEqual(browser.location, '/root')

        # Check for information.
        self.assertEqual(browser.inspect.navigation, [u'Information'])
        link = browser.inspect.navigation['information']
        self.assertEqual(link.url, 'http://localhost/root/info')

        browser.login('viewer', 'viewer')
        self.assertEqual(browser.open('http://localhost/root'), 200)

        # As viewer we should see information and product.
        self.assertEqual(
            browser.inspect.navigation,
            [u'Information', u'Product'])
        link = browser.inspect.navigation['information']
        self.assertEqual(link.url, 'http://localhost/root/info')
        link = browser.inspect.navigation['product']
        self.assertEqual(link.url, 'http://localhost/root/product')
        self.assertEqual(link.click(), 200)

    def test_preview(self):
        """In preview, we see not yet published content.
        """
        browser = self.layer.get_browser(public_settings)

        # Access preview. We need to be reader for it.
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 401)

        # Viewer can't see a thing
        browser.login('viewer', 'viewer')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 401)

        # Author should be able to acess
        browser.login('author', 'author')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 200)
        self.assertEqual(browser.location, '/root/++preview++')

        # We should see information, contact and product.
        self.assertEqual(
            browser.inspect.navigation,
            [u'Information', u'contact', u'Product'])
        link = browser.inspect.navigation['information']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/info')
        link = browser.inspect.navigation['contact']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/contact')
        link = browser.inspect.navigation['product']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/product')

        # Chief editor can see more.
        browser.login('chiefeditor', 'chiefeditor')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 200)
        self.assertEqual(browser.location, '/root/++preview++')

        self.assertEqual(
            browser.inspect.navigation,
            [u'Information', u'contact', u'Product', u'specs'])
        link = browser.inspect.navigation['information']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/info')
        link = browser.inspect.navigation['contact']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/contact')
        link = browser.inspect.navigation['product']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/product')
        link = browser.inspect.navigation['specs']
        self.assertEqual(link.url, 'http://localhost/root/++preview++/specs')
        self.assertEqual(link.click(), 200)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentNavigationTestCase))
    suite.addTest(unittest.makeSuite(ContainerNavigationTestCase))
    return suite
