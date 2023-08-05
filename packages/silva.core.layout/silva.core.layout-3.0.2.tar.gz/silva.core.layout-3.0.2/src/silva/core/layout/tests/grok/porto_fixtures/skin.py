# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from silva.core.layout.interfaces import ISilvaSkin
from silva.core.layout.porto import porto
from silva.core.layout.porto.interfaces import IPorto
from silva.core.views import views as silvaviews


class INewTheme(IPorto):
    """Layer for the theme.
    """

class INewThemeSkin(INewTheme, ISilvaSkin):
    """Skin for the new theme.
    """
    grok.skin("New theme")


grok.layer(INewTheme)


class Layout(porto.Layout):
    """Skins should have a Layout class
    """


class AwesomeView(silvaviews.Page):
    """A view
    """
    grok.name('awesome.html')

    def render(self):
        return u"Hello awesome!"
