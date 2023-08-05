# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized

from silva.core.layout.interfaces import ICustomizableLayer
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import ErrorHeaders

grok.layer(ICustomizableLayer)


# 404 page

class NotFoundPage(silvaviews.Page):
    grok.context(INotFound)
    grok.name('error.html')


class NotFoundHeaders(ErrorHeaders):
    grok.adapts(ICustomizableLayer, INotFound)

    def other_headers(self, headers):
        super(NotFoundHeaders, self).other_headers(headers)
        self.response.setStatus(404)


# Unauthorized page

class UnauthorizedPage(silvaviews.Page):
    grok.context(IUnauthorized)
    grok.name('error.html')


class UnauthorizedHeaders(ErrorHeaders):
    grok.adapts(ICustomizableLayer, IUnauthorized)

    def other_headers(self, headers):
        super(UnauthorizedHeaders, self).other_headers(headers)
        self.response.setHeader('WWW-Authenticate', 'basic realm="Zope"')
        self.response.setStatus(401)


# Other error

class OtherErrorPage(silvaviews.Page):
    grok.context(Exception)
    grok.name('error.html')


class OtherErrorHeaders(ErrorHeaders):
    grok.adapts(ICustomizableLayer, Exception)

    def other_headers(self, headers):
        super(OtherErrorHeaders, self).other_headers(headers)
        self.response.setStatus(500)
