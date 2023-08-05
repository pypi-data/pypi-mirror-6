# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner
from App.class_init import InitializeClass
import Acquisition

from five import grok
from zope.interface import Interface
from silva.core.layout.legacy.interfaces import ILegacyLayer
from silva.core.views import views as silvaviews

grok.layer(ILegacyLayer)


class LegacyCompatWrapper(Acquisition.Implicit):
    """ Wrapper object to provides compatibility with legacy templates
    """
    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, page):
        self.page = page

    security.declareProtected('View', 'view')
    def view(self):
        return self.page.content()


InitializeClass(LegacyCompatWrapper)


def wrap_context(context, view):
    return LegacyCompatWrapper(view).__of__(aq_inner(context))


class LegacyLayout(silvaviews.Layout):
    grok.context(Interface)

    def render(self):
        # We look for templates in ZODB and render it
        is_overrided = hasattr(aq_base(self.context), 'override.html')
        template_name = is_overrided and 'override.html' or 'index_html'
        context = wrap_context(self.context.get_silva_object(), self.view)
        if not hasattr(context, template_name):
            self.response.setStatus(500)
            return u'<html><body><p>(Legacy layout is missing or not installed)</p>%s</body></html>' % (
                self.view.content())

        template = getattr(context, template_name)
        if not callable(template):
            # In some cases, the template `index_html` will be None
            # (on page templates ...). In that case, we assume that
            # anyway we are not on a valid Silva content and return
            # the message with some basic layout.
            return u'<html><body>%s</body></html>' % (
                self.view.content())

        return template()


