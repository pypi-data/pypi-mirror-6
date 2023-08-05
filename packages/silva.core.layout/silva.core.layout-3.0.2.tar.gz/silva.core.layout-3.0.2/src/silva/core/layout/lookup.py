# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from AccessControl import ModuleSecurityInfo

from five import grok
from zope.component import getUtility, queryUtility, getUtilitiesFor
from zope.publisher.interfaces.browser import IBrowserSkinType

from silva.core.interfaces import IPublication
from silva.core.layout.interfaces import ISilvaSkin
from silva.core.layout.interfaces import ISkinLookup
from silva.core.services.interfaces import IMetadataService


class SilvaSkinLookup(grok.Adapter):
    grok.provides(ISkinLookup)
    grok.implements(ISkinLookup)
    grok.context(IPublication)

    def __init__(self, context):
        self.context = context
        self.get_metadata = getUtility(IMetadataService).getMetadataValue

    def get_skin(self, request):
        try:
            skin_name = self.get_metadata(self.context, 'silva-layout', 'skin')
        except AttributeError:
            # AttributeError means that the silva-layout metadata set
            # was not installed
            return None
        return queryUtility(IBrowserSkinType, name=skin_name)


module_security = ModuleSecurityInfo('silva.core.layout.lookup')
module_security.declarePublic('get_available_skins')
def get_available_skins():
    skins = getUtilitiesFor(IBrowserSkinType)
    names = [name for name, skin in skins if skin.extends(ISilvaSkin)]
    return sorted(set(names))
