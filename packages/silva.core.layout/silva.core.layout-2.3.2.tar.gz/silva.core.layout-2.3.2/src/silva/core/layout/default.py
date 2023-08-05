# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.views import views as silvaviews
from zope.interface import Interface
from silva.core.layout.interfaces import ISilvaLayer

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

    def render(self):
        return self.context.view()


