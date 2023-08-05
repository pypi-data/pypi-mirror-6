# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getUtility, getAdapter
from zope.cachedescriptors.property import Lazy
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import IContainer
from silva.core.layout.interfaces import IMetadata
from silva.core.layout.porto.interfaces import IPorto
from silva.core.services.interfaces import IContentFilteringService
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IVirtualSite

grok.layer(IPorto)


# Main design

class MainLayout(silvaviews.Layout):
    """ This is the main layout it is the first entry point of the page.

    DO NOT USE IT DIRECTLY !!

    Use Layout/Body content provider for your themes
    which permits you to customize the body of the page.
    To include your javascript and css in the head html tag
    use silva.resourceinclude
    """
    grok.template('mainlayout')
    doctype = '<!DOCTYPE html>'

    def update(self):
        self.body_id = self.context.getId().replace('.', '-')
        self.title = self.context.get_title_or_id()

    @Lazy
    def metadata(self):
        return IMetadata(self.context)

    @Lazy
    def root(self):
        virtual_site = getAdapter(self.request, IVirtualSite)
        return virtual_site.get_root()

    @Lazy
    def root_url(self):
        return absoluteURL(self.root, self.request)


class MainErrorLayout(MainLayout):
    grok.context(Exception)

    def update(self):
        self.context = self.context.get_silva_object()
        super(MainErrorLayout, self).update()


class HTMLHeadInsert(silvaviews.ViewletManager):
    """Extra elements to be inserted in the HTML Head.
    """
    pass


class Favicon(silvaviews.Viewlet):
    """ Favicon content provider.
    """
    grok.viewletmanager(HTMLHeadInsert)
    grok.name('favicon')
    grok.template('favicon')

    @property
    def favicon_url(self):
        return self.static['favicon.ico']()


class Layout(silvaviews.ContentProvider):
    """Layout for the page's body.

    This is the body part of the page.
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

    @Lazy
    def filter_entries(self):
        return getUtility(IContentFilteringService).filter(self.request)

    @Lazy
    def navigation_current(self):
        return self.context.aq_base

    def navigation_css_class(self, info, depth):
        # CSS class on li
        css_class = ['level-%d' % depth]
        if info['onbranch'] or info['current']:
            css_class.append('selected')
        return ' '.join(css_class)

    def navigation_link_css_class(self, info, depth):
        # CSS class on a
        if info['current']:
            return 'selected'
        if info['onbranch']:
            return 'onbranch'
        return None

    def navigation_entries(self, node, depth=0, maxdepth=None):
        if maxdepth is None:
            maxdepth = self.max_depth
        info = {'url': absoluteURL(node, self.request),
                'title': node.get_short_title(),
                'nodes': None,
                'onbranch': node in self.request.PARENTS,
                'current': node.aq_base == self.navigation_current}
        if depth < maxdepth and IContainer.providedBy(node):
            if ((self.only_container is not None and
                 depth < self.only_container) or info['onbranch']):
                children = self.filter_entries(node.get_ordered_publishables())
                info['nodes'] = list(children)
        return info

    @Lazy
    def navigation_root(self):
        node = self.context.get_publication()
        return list(self.filter_entries(node.get_ordered_publishables()))


class Footer(silvaviews.ContentProvider):
    """Site footer.
    """
    pass
