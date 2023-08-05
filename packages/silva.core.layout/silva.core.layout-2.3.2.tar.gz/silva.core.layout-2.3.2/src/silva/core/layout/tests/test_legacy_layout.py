# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.install import configureLegacyLayout
from Products.Silva.testing import FunctionalLayer, smi_settings
from Products.SilvaMetadata.interfaces import IMetadataService

from zope.component import getUtility


def legacy_settings(browser):
    browser.inspect.add(
        'breadcrumbs',
        xpath='//span[@class="breadcrumb"]/a',
        type='link')


class InstallationLegacyLayoutTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

    def test_installation(self):
        """Test the layout can be installed.
        """
        self.assertFalse('content.html' in self.root.objectIds())

        browser = self.layer.get_browser(smi_settings)
        browser.login('manager')
        self.assertEqual(
            browser.open('/root/service_extensions/manage_extensions'),
            200)

        form = browser.get_form('Silva')
        self.assertTrue(
            'install legacy layout' in form.inspect.actions)
        self.assertEqual(
            form.inspect.actions['install legacy layout'].click(),
            200)
        self.assertEqual(
            browser.inspect.zmi_feedback,
            ['Default legacy layout code installed'])
        self.assertTrue('content.html' in self.root.objectIds())

    def test_activation(self):
        """Test activating the layout in the metadata set.
        """
        browser = self.layer.get_browser(smi_settings)
        browser.login('manager')
        self.assertEqual(
            browser.open('/root/edit/tab_settings'),
            200)
        form = browser.get_form('form')
        control = form.get_control('silva-layout.skin:record')
        self.assertTrue('SilvaLegacy' in control.options)
        control.value = 'SilvaLegacy'
        self.assertTrue('save' in form.inspect.actions)
        self.assertEqual(form.inspect.actions['save'].click(), 200)

        metadata = getUtility(IMetadataService).getMetadata(self.root)
        self.assertEqual(metadata.get('silva-layout', 'skin'), 'SilvaLegacy')


class LegacyLayoutTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        configureLegacyLayout(self.root, True)
        metadata = getUtility(IMetadataService).getMetadata(self.root)
        metadata.setValues('silva-layout', {'skin': 'SilvaLegacy'})

    def test_render(self):
        """Test that the layout can be used to render content.
        """
        browser = self.layer.get_browser(legacy_settings)
        self.assertEqual(browser.open('/root'), 200)

        # It is difficult to test for the legacy layout. Just assume
        # one of its comments is there.
        self.assertTrue('<!-- Start Silva content -->' in browser.contents)
        self.assertEqual(browser.inspect.breadcrumbs, ['root'])

    def test_not_found(self):
        """Test the legacy layout with a not found error.
        """
        browser = self.layer.get_browser(legacy_settings)
        self.assertEqual(browser.open('/root/index/somewhere'), 404)

        # It is difficult to test for the legacy layout. Just assume
        # one of its comments is there.
        self.assertTrue('<!-- Start Silva content -->' in browser.contents)
        self.assertEqual(browser.inspect.breadcrumbs, ['root'])

        # Test for error message.
        # XXX this should use inspect.
        self.assertEqual(
            browser.html.xpath(
                'normalize-space(//div[contains(@class, "not-found")]/h1/text())'),
            'Content not found')

    def test_not_silva_content_error(self):
        """If there is an error not on a Silva content type, we still
        should see the proper layout.
        """
        factory = self.root.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        # A script with an error
        self.root.script.write('return notdefined')

        browser = self.layer.get_browser(legacy_settings)
        self.assertEqual(browser.open('/root/script'), 500)

        # It is difficult to test for the legacy layout. Just assume
        # one of its comments is there.
        self.assertTrue('<!-- Start Silva content -->' in browser.contents)
        self.assertEqual(browser.inspect.breadcrumbs, ['root'])

        self.assertEqual(
            browser.html.xpath(
                'normalize-space(//div[contains(@class, "public")]/h1/text())'),
            'Sorry')

    def test_layout_script_not_found(self):
        """If there is an error not on a Silva content type, we still
        should see the proper layout.
        """
        factory = self.root.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('script')
        # A script with an error
        self.root.script.write('return "42"')

        browser = self.layer.get_browser(legacy_settings)
        self.assertEqual(browser.open('/root/content.html/notfound'), 500)
        self.assertEqual(browser.inspect.breadcrumbs, ['root'])

        # It is difficult to test for the legacy layout. Just assume
        # one of its comments is there.
        self.assertTrue('<!-- Start Silva content -->' in browser.contents)

        self.assertEqual(
            browser.html.xpath(
                'normalize-space(//div[contains(@class, "public")]/h1/text())'),
            'Sorry')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(InstallationLegacyLayoutTestCase))
    suite.addTest(unittest.makeSuite(LegacyLayoutTestCase))
    return suite
