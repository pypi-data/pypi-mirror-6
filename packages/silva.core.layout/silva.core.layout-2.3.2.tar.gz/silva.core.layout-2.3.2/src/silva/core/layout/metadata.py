# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

# Zope 2
from AccessControl import getSecurityManager

# Silva
from Products.Silva.SilvaPermissions import ChangeSilvaContent

from silva.core.layout import interfaces
from silva.core import interfaces as silva_interfaces
from silva.core.views.interfaces import IPreviewLayer


class Metadata(grok.Adapter):
    grok.implements(interfaces.IMetadata)
    grok.provides(interfaces.IMetadata)
    grok.context(silva_interfaces.ISilvaObject)

    def __init__(self, context):
        super(Metadata, self).__init__(context)
        self._metadataservice = self.context.service_metadata
        self._content = None
        # XXX Should be a view
        # XXX Should be the previewable version ?
        if IPreviewLayer.providedBy(context.REQUEST):
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
        return self._metadataservice.getMetadataValue(
            self._content, setname, elementname)


class GhostMetadata(Metadata):
    """Apparently getMetadataValue does not work with Ghosts.

    This is because Ghosts get custom access handlers and generally are
    very magic. We work around this by using the non-fast-path in the
    metadata system which should work properly with Ghosts.
    """
    grok.context(silva_interfaces.IGhostAware)

    def __init__(self, context):
        super(GhostMetadata, self).__init__(context)
        if self._content is None:
            self._binding = None
        else:
            self._binding = self._metadataservice.getMetadata(self._content)

    def _getValue(self, setname, elementname):
        if self._binding is None:
            return None
        return self._binding.get(setname, elementname)


class MetadataSet(object):
    grok.implements(interfaces.IMetadataSet)

    def __init__(self, metadata, setid):
        self.metadata = metadata
        self.setid = setid

    def __getitem__(self, elementid):
        return self.metadata._getValue(self.setid, elementid)

