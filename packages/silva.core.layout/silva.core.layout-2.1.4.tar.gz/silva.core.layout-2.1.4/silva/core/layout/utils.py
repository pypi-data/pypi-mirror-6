# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.app.component.interfaces import ISite
from zope.traversing.interfaces import IContainmentRoot
from zope.interface import implementedBy, providedBy, Interface
from zope import component

from Acquisition import aq_parent, aq_inner


def getParent(item):
    """Return the parent item of a given item or None.
    """
    if IContainmentRoot.providedBy(obj):
        return None

    parent = getattr(obj, '__parent__', None)
    if parent is not None:
        return parent

    parent = aq_parent(aq_inner(obj))
    if parent is not None:
        return parent

    raise ValueError


def findSite(container):
    """Return the nearest site.
    """

    if ISite.providedBy(container):
        return container
    return findNextSite(container)


def findNextSite(container):
    """Return the next site.
    """
    while container:
        if IContainmentRoot.providedBy(container):
            return None
        try:
            container = getParent(container)
            if container is None:
                return None
        except TypeError:
            return None
        if ISite.providedBy(container):
            return container


def queryAdapterOnClass(klass, interface=None, name=u''):
    """Query an adapter on a klass instead of an instead of it.
    """
    sm = component.getGlobalSiteManager()
    required = implementedBy(klass)
    factory = sm.adapters.lookup((required,), interface, name)
    if factory is not None:
        result = factory(klass)
        if result is not None:
            return result
    return None


def queryMultiAdapterWithInterface(adapts, obj, interface=None, name=u""):
    """Query a multiple adapter, where the first is already an
    interface. You have to provides the object you want to replace the
    interface when the adapter is build.
    """
    sm = component.getGlobalSiteManager()
    adapts = list(adapts)
    required = [adapts[0], ] + [providedBy(k) for k in adapts[1:]]
    if interface is None:
        interface = Interface
    factory = sm.adapters.lookup(required, interface, name)
    if factory is not None:
        args = [obj, ] + adapts[1:]
        result = factory(*args)
        if result is not None:
            return result
    return None
