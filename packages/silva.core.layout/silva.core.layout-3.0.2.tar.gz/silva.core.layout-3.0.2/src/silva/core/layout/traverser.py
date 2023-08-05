# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging

from five import grok
from zope.interface import directlyProvidedBy, directlyProvides
from zope.event import notify
from zope.publisher.browser import SkinChangedEvent
from zope.traversing import namespace

from ZPublisher.interfaces import IPubStart
from infrae.wsgi.interfaces import IPublicationBeforeError
from infrae.wsgi.interfaces import IPublicationAfterTraversal

from silva.core.views.traverser import SilvaPublishTraverse
from silva.core.layout.interfaces import ICustomizableLayer, ISkinLookup


logger = logging.getLogger('silva.core.layout')

def applySkinButKeepSome(request, skin):
    # Known interfaces
    ifaces = [iface for iface in directlyProvidedBy(request)
              if not iface.extends(ICustomizableLayer)]
    # Add the new skin.
    ifaces.append(skin)
    directlyProvides(request, *ifaces)
    notify(SkinChangedEvent(request))

# This flag is set on the request during *real* traversing
# to set skin only during this process. Not when traversing
# in templates on other areas.
SET_SKIN_ALLOWED_FLAG = 'SILVA_SET_SKIN_ALLOWED'

@grok.subscribe(IPubStart)
def set_skin_flag_on(event):
    event.request[SET_SKIN_ALLOWED_FLAG] = True

@grok.subscribe(IPublicationBeforeError)
@grok.subscribe(IPublicationAfterTraversal)
def set_skin_flag_off(event):
    event.request[SET_SKIN_ALLOWED_FLAG] = False


class SkinSetterMixin(object):

    def _set_skin(self, request):
        """Set skin if necessary
        """
        if not request.get(SET_SKIN_ALLOWED_FLAG):
            return

        skin_lookup = ISkinLookup(self.context, None)
        if skin_lookup is not None:
            skin = skin_lookup.get_skin(request)
            if skin is not None:
                # We found a skin to apply
                applySkinButKeepSome(request, skin)


class SkinnyTraverser(SilvaPublishTraverse, SkinSetterMixin):

    def publishTraverse(self, request, name):
        self._set_skin(request)
        return super(SkinnyTraverser, self).publishTraverse(request, name)

    def browserDefault(self, request):
        self._set_skin(request)
        return super(SkinnyTraverser, self).browserDefault(request)


class SkinnyTraversable(SkinSetterMixin):

    def traverse(self, name, furtherPath):
        self._set_skin(self.request)
        return super(SkinnyTraversable, self).traverse(name, furtherPath)


class ResourceSkinnyTraversable(SkinnyTraversable, namespace.resource):
    pass


class ViewSkinnyTraversable(SkinnyTraversable, namespace.view):
    pass

