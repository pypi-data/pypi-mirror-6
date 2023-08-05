# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.layout.interfaces import ISilvaLayer, ISilvaSkin
from silva.core import conf as silvaconf


class ILegacyLayer(ISilvaLayer):
    """ Legacy layer
    """


class ILegacySkin(ILegacyLayer, ISilvaSkin):
    """ Legacy Skin
    """
    silvaconf.skin('SilvaLegacy')
