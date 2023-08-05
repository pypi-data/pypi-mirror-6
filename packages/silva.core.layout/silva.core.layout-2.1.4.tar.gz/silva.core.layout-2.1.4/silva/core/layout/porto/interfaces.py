# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface
from silva.core.layout.interfaces import ISilvaLayer, ISilvaSkin
from five import grok


class IDefaultLayoutRenderable(Interface):
    """Object marked by this interface can be rendered using a default
    layout.
    """

class IPorto(ISilvaLayer):
    """A layer from Porto.
    """


class IPortoWithCSS(IPorto):
    """With Silva CSS
    """


class IPortoSkin(IPortoWithCSS, ISilvaSkin):
    """A skin from Porto.
    """

    grok.skin('Porto')
