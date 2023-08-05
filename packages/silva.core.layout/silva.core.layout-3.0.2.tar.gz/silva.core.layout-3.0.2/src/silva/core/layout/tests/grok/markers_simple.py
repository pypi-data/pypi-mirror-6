# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

  First let's create a folder to play with our marker:

    >>> browser = getBrowser()
    >>> root = getRootFolder()
    >>> factory = root.manage_addProduct['Silva']
    >>> folder = factory.manage_addFolder('folder', 'Folder')

  Our purpose is to add a template called `photo`:

    >>> browser.open('http://localhost/root/folder/photo')
    404

  We can grok our marker:

    >>> grok('silva.core.layout.tests.grok.markers_simple')

  So now we should have it:

    >>> from silva.core.layout.interfaces import IMarkManager
    >>> from silva.core.layout.tests.grok.markers_simple import IPhotoFolderTag

    >>> manager = IMarkManager(folder)
    >>> sorted(manager.availableMarkers)
    [<InterfaceClass silva.core.layout.interfaces.ICustomizableMarker>,
     <InterfaceClass silva.core.views.interfaces.IDisableBreadcrumbTag>,
     <InterfaceClass silva.core.views.interfaces.IDisableNavigationTag>,
     <InterfaceClass silva.core.layout.tests.grok.markers_simple.IPhotoFolderTag>]
    >>> manager.usedMarkers
    []
    >>> IPhotoFolderTag.providedBy(folder)
    False
    >>> manager.add_marker(
    ...    u'silva.core.layout.tests.grok.markers_simple.IPhotoFolderTag')

  And it will be available on the object:

    >>> manager = IMarkManager(folder)
    >>> sorted(manager.availableMarkers)
    [<InterfaceClass silva.core.layout.interfaces.ICustomizableMarker>,
     <InterfaceClass silva.core.views.interfaces.IDisableBreadcrumbTag>,
     <InterfaceClass silva.core.views.interfaces.IDisableNavigationTag>]
    >>> sorted(manager.usedMarkers)
    [<InterfaceClass silva.core.layout.tests.grok.markers_simple.IPhotoFolderTag>]
    >>> IPhotoFolderTag.providedBy(folder)
    True
    >>> browser.open('http://localhost/root/folder/photo')
    200
    >>> browser.location
    '/root/folder/photo'
    >>> print browser.contents
    <html><body>Photo !</body></html>

  And we can remove it:

    >>> manager.remove_marker(
    ...       u'silva.core.layout.tests.grok.markers_simple.IPhotoFolderTag')

  It won't exists anymore:

    >>> manager = IMarkManager(folder)
    >>> sorted(manager.availableMarkers)
    [<InterfaceClass silva.core.layout.interfaces.ICustomizableMarker>,
     <InterfaceClass silva.core.views.interfaces.IDisableBreadcrumbTag>,
     <InterfaceClass silva.core.views.interfaces.IDisableNavigationTag>,
     <InterfaceClass silva.core.layout.tests.grok.markers_simple.IPhotoFolderTag>]
    >>> manager.usedMarkers
    []
    >>> IPhotoFolderTag.providedBy(folder)
    False
    >>> browser.open('http://localhost/root/folder/photo')
    404


  And we remove our marker from the ZCA so others tests don't fail.
  XXX We have to found something better than that:

    >>> from zeam.component import getSite
    >>> from zope.interface import Interface
    >>> from silva.core.layout.interfaces import ICustomizableType

    >>> getSite().unregister(
    ...    (Interface,),
    ...    ICustomizableType,
    ...    u'silva.core.layout.tests.grok.markers_simple.IPhotoFolderTag')

"""

from silva.core.layout.interfaces import ICustomizableTag
from silva.core.views import views as silvaviews
from five import grok


class IPhotoFolderTag(ICustomizableTag):
    """Customization tag to get a folder as a photo folder.
    """


# We could have used a template. But it needs a layout. So instead we
# define a view, and set a name. In normal use-case you would use a
# template with a layout.
class Photo(silvaviews.View):
    grok.name('photo')
    grok.context(IPhotoFolderTag)

    def render(self):
        return u'<html><body>Photo !</body></html>'
