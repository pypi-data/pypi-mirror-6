# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized

from silva.core.layout.interfaces import ICustomizableLayer
from silva.core.views import views as silvaviews

grok.layer(ICustomizableLayer)


# 404 page

class ErrorPage(silvaviews.Page):
    grok.context(INotFound)
    grok.name('error.html')

    def update(self):
        self.response.setStatus(404)


# Unauthorized page

class UnauthorizedPage(silvaviews.Page):
    grok.context(IUnauthorized)
    grok.name('error.html')

    def update(self):
        self.response.setStatus(401)
        self.response.setHeader('WWW-Authenticate', 'basic realm="Zope"')


# Other error

class OtherErrorPage(silvaviews.Page):
    grok.context(Exception)
    grok.name('error.html')

    def update(self):
        self.response.setStatus(500)
