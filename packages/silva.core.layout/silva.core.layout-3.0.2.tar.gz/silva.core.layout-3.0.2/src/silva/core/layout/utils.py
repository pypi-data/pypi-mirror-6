# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from zope.location.interfaces import ISite
from zope.traversing.interfaces import IContainmentRoot
from zope.interface import implementedBy
from zope import component

from five.localsitemanager.utils import get_parent

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
            container = get_parent(container)
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
