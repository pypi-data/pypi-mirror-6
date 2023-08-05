# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getUtility

# Zope 2
from AccessControl import getSecurityManager

# Silva
from Products.Silva.SilvaPermissions import ChangeSilvaContent

from silva.core import interfaces as silva_interfaces
from silva.core.layout import interfaces
from silva.core.services.interfaces import IMetadataService
from silva.core.views.interfaces import IPreviewLayer


class Metadata(grok.Adapter):
    grok.implements(interfaces.IMetadata)
    grok.provides(interfaces.IMetadata)
    grok.context(silva_interfaces.ISilvaObject)

    def __init__(self, context):
        super(Metadata, self).__init__(context)
        self._service = getUtility(IMetadataService)
        self._content = None
        # XXX Should be a view
        # XXX Should be the previewable version ?
        if (hasattr(context, 'REQUEST') and
            IPreviewLayer.providedBy(context.REQUEST)):
            sm = getSecurityManager()
            if sm.checkPermission(ChangeSilvaContent, context):
                self._content = context.get_editable()
        if self._content is None:
            self._content = context.get_viewable()

    def __call__(self, setid, elementid):
        return self._getValue(setid, elementid)

    def __getitem__(self, setid):
        return MetadataSet(self, setid)

    def _getValue(self, setname, elementname):
        if self._content is None:
            return None
        return self._service.getMetadataValue(
            self._content, setname, elementname)


class MetadataSet(object):
    grok.implements(interfaces.IMetadataSet)

    def __init__(self, metadata, setid):
        self.metadata = metadata
        self.setid = setid

    def __getitem__(self, elementid):
        return self.metadata._getValue(self.setid, elementid)

