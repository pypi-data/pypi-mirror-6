# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Python
from os.path import basename
import unittest

# Zope 3
from zope.component import getUtility
from zope.interface.verify import verifyObject
from zope.location.interfaces import ISite

# Zope 2
from zExceptions import BadRequest
from five.localsitemanager import make_objectmanager_site

# Silva
from silva.core.layout.interfaces import (
    ICustomizationService, IViewManager, IViewInfo)
from silva.core.layout.porto.interfaces import IPorto
from silva.core.interfaces.content import IContainer

from Products.Silva.testing import FunctionalLayer


class CustomizationTestCase(unittest.TestCase):
    """Set up a customization service before running the test.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')
        self.utility = getUtility(ICustomizationService)


class CustomizationServiceTestCase(CustomizationTestCase):
    """Test service customization setup and methods.
    """

    def test_utility_only_in_local_site(self):
        # A service_customization can be added only in a local site.
        self.assertTrue(ISite.providedBy(self.root))

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')
        self.publication = self.root.publication

        self.assertFalse(ISite.providedBy(self.publication))
        factory = self.publication.manage_addProduct['silva.core.layout']
        self.assertRaises(BadRequest,
                          factory.manage_addCustomizationService,
                          'service_customization')

        # Now our publication become a local site.
        make_objectmanager_site(self.publication)
        self.assertTrue(ISite.providedBy(self.publication))
        factory = self.publication.manage_addProduct['silva.core.layout']
        factory.manage_addCustomizationService('service_customization')
        self.assertTrue(hasattr(self.publication, 'service_customization'))

    def test_utility(self):
        self.assertTrue(hasattr(self.root, 'service_customization'))

        # Now we can fetch it
        utility = getUtility(ICustomizationService)
        self.assertTrue(verifyObject(ICustomizationService, utility))

    def test_utility_available_interfaces(self):
        self.assertTrue(hasattr(self.root, 'service_customization'))
        utility = getUtility(ICustomizationService)

        # We can list availables interfaces
        someDefaultInterfaces =  [
            u'silva.core.interfaces.content.IAsset',
            u'silva.core.interfaces.content.IContainer',
            u'silva.core.interfaces.content.IContent',
            u'silva.core.interfaces.content.IFile',
            u'silva.core.interfaces.content.IFolder',
            u'silva.core.interfaces.content.IPublication',
            u'silva.core.interfaces.content.IRoot',
            u'silva.core.interfaces.content.IViewableObject',
            u'silva.core.interfaces.content.IVersionedContent',
            u'silva.core.layout.interfaces.ICustomizableMarker',
            u'silva.core.views.interfaces.ICustomizableTag']

        foundInterfaces = utility.availablesInterfaces()
        for iface in someDefaultInterfaces:
            self.assertTrue(
                iface in foundInterfaces,
                msg='Missing interface %s' % iface)

        # We can restrain it to a sub set
        containerDefaultInterfaces = [
            u'silva.core.interfaces.content.IContainer',
            u'silva.core.interfaces.content.IFolder',
            u'silva.core.interfaces.content.IPublication',
            u'silva.core.interfaces.content.IRoot',]

        foundInterfaces = utility.availablesInterfaces(base=IContainer)
        for iface in containerDefaultInterfaces:
            self.assertTrue(
                iface in foundInterfaces,
                msg='Missing container interface %s' % iface)

    def test_utility_available_layers(self):
        self.assertTrue(hasattr(self.root, 'service_customization'))
        utility = getUtility(ICustomizationService)

        # Same goes for layers
        expected_layers = [
            u'silva.core.layout.interfaces.ISilvaLayer',
            u'silva.core.layout.porto.interfaces.IPorto',
            u'silva.core.layout.porto.interfaces.IPortoWithCSS',
            u'zope.publisher.interfaces.browser.IDefaultBrowserLayer']

        foundLayers = utility.availablesLayers()
        for iface in expected_layers:
            self.assertTrue(iface in foundLayers,
                "layer %s not available in %s" % (iface, foundLayers))

        # We can restrain it to a sub set
        silvaNewStyleLayers = [
            u'silva.core.layout.porto.interfaces.IPorto',
            u'silva.core.layout.porto.interfaces.IPortoWithCSS',]

        foundLayers = utility.availablesLayers(base=IPorto)
        for iface in silvaNewStyleLayers:
            self.assertTrue(iface in foundLayers)

    def test_view_manager(self):
        # We are going to create a folder, and a document
        utility = getUtility(ICustomizationService)
        manager = IViewManager(utility)
        self.assertTrue(verifyObject(IViewManager, manager))


class ViewEntryTestCase(CustomizationTestCase):
    """Test ViewEntry lookup and objects.
    """

    # XXX There are no testing material at the moment
    # def test_five_template(self):
    #     signature = "zope.interface.Interface:five_template:None:" \
    #         "silva.core.interfaces.content.ISilvaObject:" \
    #         "zope.publisher.interfaces.browser.IDefaultBrowserLayer"
    #     manager = IViewManager(self.utility)
    #     view = manager.from_signature(signature)
    #     self.assertFalse(view is None)
    #     self.assertTrue(verifyObject(IViewInfo, view))
    #     self.assertEqual(view.type_, 'Five Page Template')
    #     self.assertEqual(view.name, 'five_template')
    #     self.assertEqual(
    #         view.for_,
    #         'silva.core.interfaces.content.ISilvaObject')
    #     self.assertEqual(
    #         view.layer,
    #         'zope.publisher.interfaces.browser.IDefaultBrowserLayer')
    #     self.assertEqual(basename(view.template), 'smi_template.pt')
    #     self.assertEqual(view.origin, None)
    #     self.assertEqual(manager.get_signature(view), signature)

    def test_grok_template(self):
        signature = "zope.interface.Interface:index.html:None:" \
            "silva.core.interfaces.content.IViewableObject:" \
            "silva.core.layout.interfaces.ISilvaLayer"
        manager = IViewManager(self.utility)
        view = manager.from_signature(signature)

        self.assertFalse(view is None)
        self.assertTrue(verifyObject(IViewInfo, view))
        self.assertEqual(view.type_, 'Grok Page Template')
        self.assertEqual(view.name, 'index.html')
        self.assertEqual(
            view.for_,
            'silva.core.interfaces.content.IViewableObject')
        self.assertEqual(
            view.layer,
            'silva.core.layout.interfaces.ISilvaLayer')
        self.assertEqual(view.template, None)
        self.assertEqual(view.origin, None)
        self.assertEqual(manager.get_signature(view), signature)

    def test_grok_content_provider(self):
        signature = "zope.viewlet.interfaces.IViewletManager:footer:None:" \
            "silva.core.interfaces.content.IViewableObject:" \
            "silva.core.layout.porto.interfaces.IPorto:" \
            "zope.browser.interfaces.IBrowserView"
        manager = IViewManager(self.utility)
        view = manager.from_signature(signature)
        self.assertFalse(view is None)
        self.assertTrue(verifyObject(IViewInfo, view))
        self.assertEqual(view.type_, 'Grok Content Provider')
        self.assertEqual(view.name, 'footer')
        self.assertEqual(
            view.for_,
            'silva.core.interfaces.content.IViewableObject')
        self.assertEqual(
            view.layer,
            'silva.core.layout.porto.interfaces.IPorto')
        self.assertEqual(basename(view.template), 'footer.cpt')
        self.assertEqual(view.origin, None)
        self.assertEqual(manager.get_signature(view), signature)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CustomizationServiceTestCase))
    suite.addTest(unittest.makeSuite(ViewEntryTestCase))
    return suite
