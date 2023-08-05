# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface, Attribute
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

# Interfaces types

class ICustomizableType(IInterface):
    """This type represent customizable interface in Silva. THIS IS
    NOT AN INTERFACE TO PROVIDES OR IMPLEMENTS.
    """


class ILayerType(IInterface):
    """This type represent Silva layer. THIS NOT AND INTERFACE TO
    PROVIDES OR IMPLEMENTS.
    """


# Interfaces

class ICustomizable(Interface):
    """This content is customizable.
    """

class ICustomizableTag(ICustomizable):
    """This is a tag that you can set on object to customize them.
    """


class ICustomizableMarker(ICustomizableTag):
    """Customizable markers.
    """


# Default skin and layers

class ICustomizableLayer(IDefaultBrowserLayer):
    """A customizable layer.
    """


class ISMILayer(ICustomizableLayer):
    """SMI objects.
    """


class ISilvaLayer(ICustomizableLayer):
    """Default Silva Layer
    """


class ISilvaSkin(ISilvaLayer, IBrowserSkinType):
    """A Silva skin for the default layer.
    """

# Adapters

class IMarkManager(Interface):
    """A Mark manager. This let you manage marks on object, so they
    can be customized after using them.
    """

    usedInterfaces = Attribute(u"Skinable interfaces used")
    usedMarkers = Attribute(u"Skinable markers set on the object")
    availableMarkers = Attribute(
        u"Skinable markers that can be set  on the object")

    def addMarker(name):
        """Set marker name in the object.
        """

    def removeMarker(name):
        """Remove marker name from the object.
        """



# Events

class IObjectMarkEvent(Interface):
    """A marker have been involved with an object.
    """

    marker = Attribute(u"Involved marker")


class IObjectHaveBeenMarked(IObjectMarkEvent):
    """An object have been marked by a marker.
    """


class IObjectHaveBeenUnmarked(IObjectMarkEvent):
    """A Marker have been removed from an object.
    """

