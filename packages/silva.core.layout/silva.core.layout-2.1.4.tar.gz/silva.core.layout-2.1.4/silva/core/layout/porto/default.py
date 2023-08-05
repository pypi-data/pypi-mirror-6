# -*- coding: utf-8 -*-
# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.interfaces import ISilvaObject
from Acquisition import aq_parent

from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from silva.core.views import views as silvaviews
from five import grok

from silva.core.layout.porto.interfaces import IDefaultLayoutRenderable

grok.layer(IDefaultBrowserLayer)


class MainLayout(silvaviews.Layout):
    """This layout is designed to render Zope object which are not
    Silva ones. It will redirect you to the first SilvaObject found in
    the path.
    """
    grok.context(IDefaultLayoutRenderable)

    def render(self):
        # There is nothing to see here. Try to get to the nearest
        # Silva object.
        parent = self.context.aq_inner
        while not ISilvaObject.providedBy(parent):
            parent = aq_parent(parent)
            if parent is None:
                return u"There is nothing on that Zope object."
        self.view.redirect(parent.absolute_url())


class MainTemplate(silvaviews.Page):
    """This template is for Zope object which can be asked to be
    rendered in a layout. They have no templates by default.
    """
    grok.context(IDefaultLayoutRenderable)
    grok.name('index.html')

    def render(self):
        return "This is a Zope oject, which is not renderable in Silva."
