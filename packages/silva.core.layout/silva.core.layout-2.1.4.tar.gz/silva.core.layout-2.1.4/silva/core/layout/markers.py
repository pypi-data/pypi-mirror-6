# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.interface import PersistentInterfaceClass
from zope.app.intid.interfaces import IIntIds
from zope.component.interfaces import ObjectEvent
from zope.component import getUtility, getUtilitiesFor
from zope.interface.interfaces import IInterface
from zope.interface import providedBy, directlyProvides, directlyProvidedBy
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import Interface
from zope.event import notify
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope import schema
import zope.cachedescriptors.property

from persistent.list import PersistentList

from five import grok

from z3c.form import field, button
from z3c.form.interfaces import DISPLAY_MODE

# Zope 2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.interfaces import IObjectWillBeRemovedEvent
from OFS import SimpleItem

# Silva
from Products.Silva.helpers import add_and_edit
from Products.Silva.interfaces import ISilvaObject
from Products.Silva.browser.smi import SMIButton, PropertiesTab

from silva.core.views import views as silvaviews
from silva.core.views import z3cforms as silvaz3cforms

from interfaces import ICustomizableType, ICustomizableTag, ICustomizableMarker
from interfaces import IObjectHaveBeenMarked, IObjectHaveBeenUnmarked
from interfaces import IObjectMarkEvent, IMarkManager
from utils import findSite


# Marker object

class CustomizationMarker(PersistentInterfaceClass, SimpleItem.SimpleItem):

    meta_type = 'Silva Customization Marker'

    def __init__(self, name, doc=None):
        self.id = name
        PersistentInterfaceClass.__init__(
            self, name=name, bases=(ICustomizableMarker,), __doc__=doc)
        SimpleItem.SimpleItem.__init__(self, name)
        self.marked = PersistentList()

    def updateIdentifier(self):
        self.__identifier__ = self.markerId()

    def addMarkedObject(self, obj):
        oid = getUtility(IIntIds).register(obj)
        self.marked.append(oid)

    def removeMarkedObject(self, obj):
        oid = getUtility(IIntIds).getId(obj)
        self.marked.remove(oid)

    def markedObjects(self):
        resolver = getUtility(IIntIds).getObject
        return [resolver(oid) for oid in self.marked]

    def markerId(self):
        return u'marker:%s' % '.'.join(self.getPhysicalPath()[1:])


manage_addCustomizationMarkerForm = PageTemplateFile(
    "www/customizationMarkerAdd", globals(),
    __name__='manage_addCustomizationMarkerForm')


def manage_addCustomizationMarker(self, name, REQUEST=None):
    """Add a Customization Marker.
    """

    marker = CustomizationMarker(name)
    self._setObject(name, marker)
    add_and_edit(self, name, REQUEST)
    return ''



# Event arround markers

class ObjectMarkEvent(ObjectEvent):

    grok.implements(IObjectMarkEvent)

    def __init__(self, item, marker):
        super(ObjectMarkEvent, self).__init__(item)
        self.marker = marker


class ObjectHaveBeenMarked(ObjectMarkEvent):

    grok.implements(IObjectHaveBeenMarked)


class ObjectHaveBeenUnmarked(ObjectMarkEvent):

    grok.implements(IObjectHaveBeenUnmarked)


REGISTERED_TYPES = [IInterface, ICustomizableType,]

@grok.subscribe(CustomizationMarker, IObjectAddedEvent)
def registerMarker(marker, event):
    site = findSite(event.newParent)
    if site:
        sm = site.getSiteManager()
        marker.updateIdentifier()
        for iface_type in REGISTERED_TYPES:
            sm.registerUtility(marker, iface_type, marker.__identifier__)


@grok.subscribe(CustomizationMarker, IObjectWillBeRemovedEvent)
def unregisterMarker(marker, event):
    site = findSite(event.oldParent)
    for item in marker.markedObjects():
        IMarkManager(item).removeMarker(marker.__identifier__)
    if site:
        sm = site.getSiteManager()
        for iface_type in REGISTERED_TYPES:
            sm.unregisterUtility(marker, iface_type, marker.__identifier__)


@grok.subscribe(ISilvaObject, IObjectHaveBeenMarked)
def objectMarked(item, event):
    if event.marker.extends(ICustomizableMarker):
        event.marker.addMarkedObject(item)


@grok.subscribe(ISilvaObject, IObjectHaveBeenUnmarked)
def objectUnmarked(item, event):
    if event.marker.extends(ICustomizableMarker):
        event.marker.removeMarkedObject(item)


# Adapters

class MarkManager(grok.Adapter):

    grok.implements(IMarkManager)
    grok.context(ISilvaObject)
    grok.require('zope2.ManageProperties')

    def _listInterfaces(self, base):
        interfaces = providedBy(self.context).interfaces()
        return sorted([iface.__identifier__ for iface in interfaces
                       if iface.extends(base)])

    def _fetchMarker(self, name):
        return getUtility(ICustomizableType, name=name)

    @zope.cachedescriptors.property.CachedProperty
    def usedInterfaces(self):
        return self._listInterfaces(ISilvaObject)

    @zope.cachedescriptors.property.CachedProperty
    def usedMarkers(self):
        return self._listInterfaces(ICustomizableTag)

    @zope.cachedescriptors.property.CachedProperty
    def availableMarkers(self):
        interfaces = getUtilitiesFor(ICustomizableType, context=self.context)
        availables = [name for name, interface in interfaces
                      if interface.extends(ICustomizableTag)]
        return sorted(list(set(availables).difference(set(self.usedMarkers))))

    def removeMarker(self, name):
        marker = self._fetchMarker(name)
        directlyProvides(
            self.context, directlyProvidedBy(self.context) - marker)
        notify(ObjectHaveBeenUnmarked(self.context, marker))

    def addMarker(self, name):
        marker = self._fetchMarker(name)
        directlyProvides(
            self.context, directlyProvidedBy(self.context), marker)
        notify(ObjectHaveBeenMarked(self.context, marker))


# Forms to mark objects

@grok.provider(IContextSourceBinder)
def usedInterfacesForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary([SimpleTerm(i) for i in manager.usedInterfaces])

@grok.provider(IContextSourceBinder)
def usedMarkersForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary([SimpleTerm(i) for i in manager.usedMarkers])


@grok.provider(IContextSourceBinder)
def availableMarkersForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary([SimpleTerm(i) for i in manager.availableMarkers])


class IDisplayUsedInterfaces(Interface):

    usedInterface = schema.Set(
        title=u"Used interfaces",
        value_type=schema.Choice(
            source=usedInterfacesForContent),
        required=False)


class IRemoveCustomizationMarker(Interface):

    usedMarkers = schema.Set(
        title=u"Used markers",
        value_type=schema.Choice(
            source=usedMarkersForContent))


class IAddCustomizationMarker(Interface):

    availablesMarkers = schema.Set(
        title=u"Available markers",
        value_type=schema.Choice(
            source=availableMarkersForContent))


class ContentInterfaces(grok.Adapter):

    grok.context(ISilvaObject)
    grok.provides(IDisplayUsedInterfaces)

    @property
    def usedInterface(self):
        manager = IMarkManager(self.context)
        return manager.usedInterfaces


class ManageCustomizeMarker(silvaz3cforms.ComposedForm, PropertiesTab):

    grok.name('tab_customization')
    grok.require('silva.ChangeSilvaContent')

    label = "customization markers"
    description = "This let you marker your content with markers who are going to change how it is displayed."


class DisplayUsedInterfaces(silvaz3cforms.SubForm):

    grok.view(ManageCustomizeMarker)
    grok.order(10)

    label = "Used interfaces by the content which change its rendering"
    fields = field.Fields(IDisplayUsedInterfaces)
    mode = DISPLAY_MODE


class AddCustomizationMarker(silvaz3cforms.SubForm):

    grok.view(ManageCustomizeMarker)
    grok.order(20)

    label = "Add a marker to affect the content rendering"
    fields = field.Fields(IAddCustomizationMarker)
    ignoreContext = True

    @button.buttonAndHandler(
        u"Add", name="add",
        condition=lambda form: form.widgets['availablesMarkers'].terms)
    def handle_add(self, action):
        values, errors = self.extractData()
        if not values['availablesMarkers']:
            self.status = u"You need to select a marker."
            self.status_type = 'error'
        else:
            manager = IMarkManager(self.context)
            for value in values['availablesMarkers']:
                manager.addMarker(value)
            self.status = u"Marker added."


class RemoveCustomizationMarker(silvaz3cforms.SubForm):

    grok.view(ManageCustomizeMarker)
    grok.order(30)

    label = "Remove a marker"
    fields = field.Fields(IRemoveCustomizationMarker)
    ignoreContext = True

    @button.buttonAndHandler(
        u"Remove", name="remove",
        condition=lambda form: form.widgets['usedMarkers'].terms)
    def handle_remove(self, action):
        values, errors = self.extractData()
        if not values['usedMarkers']:
            self.status = u"You need to select a marker."
            self.status_type = 'error'
        else:
            manager = IMarkManager(self.context)
            for value in values['usedMarkers']:
                manager.removeMarker(value)
            self.status = u"Marker removed."


class ManageCustomizationButton(SMIButton):

    order = 110

    tab = 'tab_customization'
    label = "customization"
