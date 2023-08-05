# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface, Attribute
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from silva.core.interfaces.service import ISilvaLocalService
from silva.core.views.interfaces import ICustomizableTag
from silva.core.interfaces import ICustomizable

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

class ICustomizableMarker(ICustomizableTag):
    """All Customizable markers
    """


# Default skin and layers

class ICustomizableLayer(IDefaultBrowserLayer):
    """A customizable layer.
    """


class ISilvaLayer(ICustomizableLayer):
    """Default Silva Layer
    """


class ISilvaSkin(ISilvaLayer):
    """A Silva skin for the default layer.
    """


# Adapters

class ISkinLookup(Interface):

    def get_skin():
        """Return a skin to apply on the request, or None.
        """


class IMarkManager(Interface):
    """A Mark manager. This let you manage marks on object, so they
    can be customized after using them.
    """

    usedInterfaces = Attribute(u"Skinable interfaces used")
    usedMarkers = Attribute(u"Skinable markers set on the object")
    availableMarkers = Attribute(
        u"Skinable markers that can be set  on the object")

    def add_marker(marker):
        """Set marker name in the object.
        """

    def remove_marker(marker):
        """Remove marker name from the object.
        """


class IViewInfo(Interface):
    """This is a view that your are going to customize.
    """

    name = Attribute(u"Name of the view")
    type_ = Attribute(u"Kind of template type")
    template = Attribute(u"Template rendering the view")
    config = Attribute(u"Where is configured that view")
    for_ = Attribute(u"For which content is registered the view")
    layer = Attribute(u"On which layer is registered the view")
    origin = Attribute(u"Where the view is defined")
    code = Attribute(u"Code of the associated template")

    def generateId():
        """Generate ID of a possible customized template.
        """

    def permission():
        """Return the permission required to view that view/template.
        """

    def customize(where, customized_for=None, customized_layer=None):
        """Customize the template for the given site.

        If customized_for or customized_layer are given, the template
        will be customized for this entries instead of the current
        ones.
        """


class IViewManager(Interface):
    """Manages Views.
    """

    def search(interface, layer, sort=False):
        """Search all views for that interface and layer.
        """

    def get(type_, name, origin, required):
        """Search the view which match that kind, name and signature.
        """

    def from_signature(signature):
        """Load view information from a signature.
        """

    def get_signature(view_info):
        """Return a signature (string) which should uniquely identify
        the view.
        """


# Utility

class ICustomizationService(ISilvaLocalService):
    """A customization manager let you customize templates.
    """

    def availablesInterfaces(base=ICustomizable):
        """List availables interfaces, which can be used to search
        view to customize.
        """

    def availablesLayers(base=IDefaultBrowserLayer):
        """List availables layers, for which you can customize views.
        """

    def availablesTemplates(interface, layer=IDefaultBrowserLayer):
        """List availables templates for that interface and layer.
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


class IMetadata(Interface):

    def __getitem__(setname):
        pass

    def __call__(setname, elementname):
        pass

class IMetadataSet(Interface):

    def __getitem__(elementname):
        pass


class ITranslator(Interface):
    def get_available_languages():
        """Get a list of the globally available translations"""
        pass

    def has_translation(language):
        """Is the translation into language available for the context
        object"""
        pass

    def get_translation(language):
        """get the object that is the translation for context and
        language"""
        pass

    def current_language():
        """return the translation context is in if any"""
        pass

    def get_translation_url(language):
        """get the url for the object that is the translation for
        context and language"""
        pass


class ILanguageSelector(Interface):
    def __call__():
        """get the html that is displayed as the content of the link
        to the translation"""
        pass

