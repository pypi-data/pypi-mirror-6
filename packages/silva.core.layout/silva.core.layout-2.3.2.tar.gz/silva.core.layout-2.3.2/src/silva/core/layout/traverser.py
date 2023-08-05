# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from five import grok
from zope import component
from zope.interface import directlyProvidedBy, directlyProvides
from zope.event import notify
from zope.publisher.browser import SkinChangedEvent
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.traversing import namespace

from ZPublisher.interfaces import IPubAfterTraversal, IPubStart

from silva.core.views.traverser import SilvaPublishTraverse
from silva.core.layout.interfaces import ICustomizableLayer, IMetadata


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

@grok.subscribe(IPubAfterTraversal)
def set_skin_flag_off(event):
    event.request[SET_SKIN_ALLOWED_FLAG] = False


class SkinSetterMixin(object):

    def _setSkin(self, request):
        """Set skin if necessary"""

        if not request.get(SET_SKIN_ALLOWED_FLAG):
            return

        try:
            metadata = IMetadata(self.context)
        except TypeError, e:
            request.set('resourcebase', self.context)
        else:
            try:
                skin_name = metadata('silva-layout', 'skin')
            except AttributeError:
                # AttributeError means that the silva-layout metadata set
                # was not installed, so just bail out without setting any
                # skin
                return

            if skin_name:
                # Retrieve the skin object
                skin = component.queryUtility(IBrowserSkinType, name=skin_name)
                if skin is not None:
                    # Simply override any previously set skin. We have to
                    # do so in order to cover the usecase where we apply
                    # only now a skin which is used as a base for a one
                    # which was applied on a parent (otherwise we won't
                    # see the change, since it's already provided).
                    applySkinButKeepSome(request, skin)
                    # Set the base url for resources
                    request.set('resourcebase', self.context)
                else:
                    logger.error('Cannot find requested skin %s' % skin_name)


class SkinnyTraverser(SilvaPublishTraverse, SkinSetterMixin):

    def publishTraverse(self, request, name):
        self._setSkin(request)
        return super(SkinnyTraverser, self).publishTraverse(request, name)

    def browserDefault(self, request):
        self._setSkin(request)
        return super(SkinnyTraverser, self).browserDefault(request)


class SkinnyTraversable(SkinSetterMixin):

    def traverse(self, name, furtherPath):
        self._setSkin(self.request)
        return super(SkinnyTraversable, self).traverse(name, furtherPath)


class ResourceSkinnyTraversable(SkinnyTraversable, namespace.resource):
    pass


class ViewSkinnyTraversable(SkinnyTraversable, namespace.view):
    pass

