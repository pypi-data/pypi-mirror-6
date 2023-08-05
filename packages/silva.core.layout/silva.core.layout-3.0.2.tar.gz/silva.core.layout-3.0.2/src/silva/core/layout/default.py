# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.interfaces import IVersionedContent, IVersion
from silva.core.layout.interfaces import ISilvaLayer
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IView
from silva.translations import translate as _
from grokcore.layout.interfaces import ILayout
from zope.component import queryMultiAdapter, getMultiAdapter
from zope.interface import Interface
from zope.i18n import translate

from zExceptions import NotFound

grok.layer(ISilvaLayer)


class FallbackLayout(silvaviews.Layout):
    """ Layout for objects that do not provide ISilvaObject
    """
    grok.context(Interface)

    def render(self):
        return """
            <html>
                <head><!-- no layout --></head>
                <body>%s</body>
            </html>
        """ % self.view.content()


class MainPage(silvaviews.Page):
    grok.name('index.html')
    grok.require('zope2.View')

    def render(self):
        view = queryMultiAdapter(
            (self.context, self.request), name='content.html')
        if view is None:
            raise NotFound('content.html')
        if IView.providedBy(view):
            if view.content is None:
                msg = _('Sorry, this ${meta_type} is not viewable.',
                        mapping={'meta_type': self.context.meta_type})
                return '<p>%s</p>' % translate(msg, context=self.request)
        return view()


class VersionedContentMainPage(silvaviews.Page):
    grok.name('index.html')
    grok.context(IVersionedContent)
    grok.require('zope2.View')

    def render(self):
        view = queryMultiAdapter(
            (self.context, self.request), name='content.html')
        if view is None:
            raise NotFound('content.html')
        if IView.providedBy(view) and view.content is None:
            msg = _('Sorry, this ${meta_type} is not viewable.',
                    mapping={'meta_type': self.context.meta_type})
            return '<p>%s</p>' % translate(msg, context=self.request)
        return view()


class VersionMainPage(silvaviews.Page):
    grok.name('index.html')
    grok.context(IVersion)
    grok.require('silva.ReadSilvaContent')

    def render(self):
        content = self.context.get_silva_object()
        view = queryMultiAdapter(
            (content, self.request), name='content.html')
        if view is None:
            raise NotFound('content.html')
        if IView.providedBy(view):
            view.content = self.context
            return view()
        msg = _('Sorry, this ${meta_type} is not viewable.',
                mapping={'meta_type': content.meta_type})
        return '<p>%s</p>' % translate(msg, context=self.request)


# Return a layout for a version. We lookup the layout of the related content
def version_layout(request, version):
    return getMultiAdapter((request, version.get_silva_object()), ILayout)

grok.global_adapter(version_layout, (ISilvaLayer, IVersion), ILayout)
