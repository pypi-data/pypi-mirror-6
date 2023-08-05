# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.cachedescriptors.property import CachedProperty
from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized
from zope.traversing.browser import absoluteURL
from zope import component, interface

from AccessControl import getSecurityManager

from Products.Silva.interfaces import IContainer, IPublishable
from Products.SilvaLayout.interfaces import IMetadata

from silva.core.views.interfaces import IVirtualSite, IHTTPResponseHeaders
from silva.core.views import views as silvaviews
from five import grok

from silva.core.layout.porto.interfaces import IPorto

grok.layer(IPorto)

# Main design

class MainLayout(silvaviews.Layout):

    grok.template('mainlayout')

    def update(self):
        component.getMultiAdapter(
            (self.context, self.request), IHTTPResponseHeaders)()

    @CachedProperty
    def metadata(self):
        return IMetadata(self.context)

    @CachedProperty
    def root(self):
        virtual_site = component.getAdapter(self.request, IVirtualSite)
        return virtual_site.get_root()

    @CachedProperty
    def root_url(self):
        return self.root.absolute_url()


class FallbackLayout(silvaviews.Layout):
    """ Layout for objects that do not provide ISilvaObject
    """
    grok.context(interface.Interface)

    def render(self):
        return """
            <html>
                <head><!-- no layout --></head>
                <body>%s</body>
            </html>
        """ % self.view.content()


class MainTemplate(silvaviews.Page):

    grok.name('index.html')

    def render(self):
        return self.context.view()


# We need to define a preview template in 2.1.
class PreviewTemplate(silvaviews.Page):

    grok.name('preview_html')

    def render(self):
        return self.context.preview()


class Layout(silvaviews.ContentProvider):
    """Layout of the page.
    """
    pass


class Header(silvaviews.ContentProvider):
    """Define a site header.
    """
    pass


class Breadcrumbs(silvaviews.ContentProvider):
    """Breadcrumbs.
    """
    pass


class Navigation(silvaviews.ContentProvider):
    """Navigation
    """

    max_depth = 2
    only_container = None

    @CachedProperty
    def filter_service(self):
        # Should be an utility
        return self.context.service_toc_filter

    def filter_entries(self, nodes):
        checkPermission = getSecurityManager().checkPermission
        def filter_entry(node):
            # This should in the toc filter ?
            if IPublishable.providedBy(node) and not node.is_published():
                return False
            # Should be in the toc filter
            if not checkPermission('View', node):
                return False
            return not self.filter_service.filter(node)
        return filter(lambda node: filter_entry(node), nodes)

    @CachedProperty
    def navigation_current(self):
        return self.context.aq_base

    def navigation_css_class(self, info, depth):
        # CSS class on li
        css_class = ['level-%d' % depth,]
        if info['onbranch'] or info['current']:
            css_class.append('selected')
        return ' '.join(css_class)

    def navigation_link_css_class(self, info, depth):
        # CSS class on a
        return (info['onbranch'] or info['current']) and 'selected' or None

    def navigation_entries(self, node, depth=0, maxdepth=None):
        if maxdepth is None:
            maxdepth = self.max_depth
        info = {'url': absoluteURL(node, self.request),
                'title': node.get_short_title(),
                'nodes': None,
                'onbranch': node in self.request.PARENTS,
                'current': node.aq_base is self.navigation_current}
        if depth < maxdepth and IContainer.providedBy(node):
            if ((self.only_container is not None and
                 depth < self.only_container) or info['onbranch']):
                children = self.filter_entries(node.get_ordered_publishables())
                info['nodes'] = list(children)
        return info

    @CachedProperty
    def navigation_root(self):
        node = self.context.get_publication()
        return list(self.filter_entries(node.get_ordered_publishables()))


class Footer(silvaviews.ContentProvider):
    """Site footer.
    """
    pass


# 404 page

class ErrorPage(silvaviews.Page):
    grok.context(INotFound)
    grok.name('error.html')


# Unauthorized page

class UnauthorizedPage(silvaviews.Page):
    grok.context(IUnauthorized)
    grok.name('error.html')

# Other error

class OtherErrorPage(silvaviews.Page):
    grok.context(interface.Interface)
    grok.name('error.html')
