# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from persistent.list import PersistentList
from zeam.component import getAllComponents, getComponent
from zope.app.interface import PersistentInterfaceClass
from zope.component import getUtility, getUtilitiesFor
from zope.component.interfaces import ObjectEvent
from zope.container.interfaces import IObjectAddedEvent
from zope.event import notify
from zope.interface import providedBy, directlyProvides, directlyProvidedBy
from zope.interface.interfaces import IInterface
from zope.intid.interfaces import IIntIds
import zope.cachedescriptors.property

# Zope 2
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.interfaces import IObjectWillBeRemovedEvent

# Silva
from Products.Silva.helpers import add_and_edit

from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.layout.utils import findSite
from silva.core.services.base import ZMIObject

from silva.core.layout.interfaces import (
    ICustomizableType, ICustomizableTag,
    ICustomizableMarker, IObjectHaveBeenMarked, IObjectHaveBeenUnmarked,
    IObjectMarkEvent, IMarkManager)

# Marker object

class CustomizationMarker(PersistentInterfaceClass, ZMIObject):

    meta_type = 'Silva Customization Marker'

    silvaconf.icon('markers.png')
    silvaconf.factory('manage_addCustomizationMarkerForm')
    silvaconf.factory('manage_addCustomizationMarker')

    def __init__(self, name, doc=None):
        self.id = name
        PersistentInterfaceClass.__init__(
            self, name=name, bases=(ICustomizableMarker,), __doc__=doc)
        ZMIObject.__init__(self)
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
def unregister_marker(marker, event):
    site = findSite(event.oldParent)
    for item in marker.markedObjects():
        IMarkManager(item).remove_marker(marker.__identifier__)
    if site:
        sm = site.getSiteManager()
        for iface_type in REGISTERED_TYPES:
            sm.unregisterUtility(marker, iface_type, marker.__identifier__)


@grok.subscribe(ISilvaObject, IObjectHaveBeenMarked)
def object_marked(item, event):
    if event.marker.extends(ICustomizableMarker):
        event.marker.addMarkedObject(item)


@grok.subscribe(ISilvaObject, IObjectHaveBeenUnmarked)
def object_unmarked(item, event):
    if event.marker.extends(ICustomizableMarker):
        event.marker.removeMarkedObject(item)


# Adapters

class MarkManager(grok.Adapter):
    grok.implements(IMarkManager)
    grok.context(ISilvaObject)
    grok.require('zope2.ManageProperties')

    def _listInterfaces(self, base):
        interfaces = providedBy(self.context).interfaces()
        return sorted([iface for iface in interfaces
                       if iface.extends(base)])

    def _fetchMarker(self, name):
        interface = getComponent(
            (self.context,),
            provided=ICustomizableType, name=name, default=None)
        if interface is None:
            return getUtility(ICustomizableType, name=name)
        return interface

    @zope.cachedescriptors.property.CachedProperty
    def usedInterfaces(self):
        return self._listInterfaces(ISilvaObject)

    @zope.cachedescriptors.property.CachedProperty
    def usedMarkers(self):
        return self._listInterfaces(ICustomizableTag)

    @zope.cachedescriptors.property.CachedProperty
    def availableMarkers(self):
        # ZODB Makers and FS based one
        availables = []
        for source in [getUtilitiesFor(ICustomizableType, context=self.context),
                       getAllComponents(self.context, ICustomizableType)]:
            for name, iface in source:
                if iface.extends(ICustomizableTag):
                    availables.append(iface)
        return sorted(list(set(availables).difference(set(self.usedMarkers))))

    def remove_marker(self, marker):
        if isinstance(marker, basestring):
            marker = self._fetchMarker(marker)
        directlyProvides(
            self.context, directlyProvidedBy(self.context) - marker)
        notify(ObjectHaveBeenUnmarked(self.context, marker))

    def add_marker(self, marker):
        if isinstance(marker, basestring):
            marker = self._fetchMarker(marker)
        directlyProvides(
            self.context, directlyProvidedBy(self.context), marker)
        notify(ObjectHaveBeenMarked(self.context, marker))


