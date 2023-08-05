# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""

  First let's create a folder to play with our marker:

    >>> browser = Browser()
    >>> root = getRootFolder()
    >>> factory = root.manage_addProduct['Silva']
    >>> folder = factory.manage_addFolder('folder', 'Folder')

  Our purpose is to add a template called `photo`:

    >>> browser.open('http://localhost/root/folder/photo')
    Traceback (most recent call last):
      ...
    HTTPError: HTTP Error 404: Not Found

  We can grok our marker:

    >>> grok('silva.core.layout.tests.grok.markers')

  So now we should have it:

    >>> from silva.core.layout.interfaces import IMarkManager
    >>> from silva.core.layout.tests.grok.markers import IPhotoFolderTag

    >>> manager = IMarkManager(folder)
    >>> sorted(manager.availableMarkers)
    [<InterfaceClass silva.core.layout.interfaces.ICustomizableMarker>,
     <InterfaceClass silva.core.layout.tests.grok.markers.IPhotoFolderTag>,
     <InterfaceClass Products.Silva.Folder.IPhotoGallery>]
    >>> manager.usedMarkers
    []
    >>> IPhotoFolderTag.providedBy(folder)
    False
    >>> manager.addMarker(
    ...    u'silva.core.layout.tests.grok.markers.IPhotoFolderTag')

  And it will be available on the object:

    >>> manager = IMarkManager(folder)
    >>> sorted(manager.availableMarkers)
    [<InterfaceClass silva.core.layout.interfaces.ICustomizableMarker>,
     <InterfaceClass Products.Silva.Folder.IPhotoGallery>]
    >>> sorted(manager.usedMarkers)
    [<InterfaceClass silva.core.layout.tests.grok.markers.IPhotoFolderTag>]
    >>> IPhotoFolderTag.providedBy(folder)
    True
    >>> browser.open('http://localhost/root/folder/photo')
    >>> browser.status
    '200 OK'
    >>> browser.url
    'http://localhost/root/folder/photo'
    >>> print browser.contents
    <html><body>Photo !</body></html>

  And we can remove it:

    >>> manager.removeMarker(
    ...       u'silva.core.layout.tests.grok.markers.IPhotoFolderTag')

  It won't exists anymore:

    >>> manager = IMarkManager(folder)
    >>> sorted(manager.availableMarkers)
    [<InterfaceClass silva.core.layout.interfaces.ICustomizableMarker>,
     <InterfaceClass silva.core.layout.tests.grok.markers.IPhotoFolderTag>,
     <InterfaceClass Products.Silva.Folder.IPhotoGallery>]
    >>> manager.usedMarkers
    []
    >>> IPhotoFolderTag.providedBy(folder)
    False
    >>> browser.open('http://localhost/root/folder/photo')
    Traceback (most recent call last):
      ...
    HTTPError: HTTP Error 404: Not Found


  And we remove our marker from the ZCA so others tests don't fail.
  XXX We have to found something better than that:

    >>> from zope.component import getGlobalSiteManager
    >>> from silva.core.layout.interfaces import ICustomizableType
    >>> sm = getGlobalSiteManager()
    >>> sm.unregisterUtility(
    ...         IPhotoFolderTag, ICustomizableType,
    ...         u'silva.core.layout.tests.grok.markers.IPhotoFolderTag')
    True

"""

from silva.core.layout.interfaces import ICustomizableTag
from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

class IPhotoFolderTag(ICustomizableTag):
    """Customization tag to get a folder as a photo folder.
    """


# We could have used a template. But it needs a layout. So instead we
# define a view, and set a name. In normal use-case you would use a
# template with a layout.
class Photo(silvaviews.View):

    silvaconf.name('photo')
    silvaconf.context(IPhotoFolderTag)

    def render(self):
        return u'<html><body>Photo !</body></html>'
