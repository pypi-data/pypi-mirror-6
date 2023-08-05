# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope
from AccessControl import ModuleSecurityInfo

# Zope3
from zope import component
from zope.publisher.interfaces.browser import IBrowserSkinType

from silva.core.layout.interfaces import ISilvaSkin

# Helpers to integrate Zope3, Five and SilvaLayout functionality
# with Zope2 and Silva

__allow_access_to_unprotected_subobjects__ = 1

module_security = ModuleSecurityInfo('silva.core.layout.helpers')

module_security.declareProtected(
    'Access Contents Information', 'getAvailableSkins')
def getAvailableSkins():
    skins = component.getUtilitiesFor(IBrowserSkinType)
    return [name for name, skin in skins if skin.extends(ISilvaSkin)]
