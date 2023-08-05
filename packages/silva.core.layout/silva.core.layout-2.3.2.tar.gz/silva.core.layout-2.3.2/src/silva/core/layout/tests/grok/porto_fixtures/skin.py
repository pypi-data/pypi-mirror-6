# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from silva.core.layout.interfaces import ISilvaSkin
from silva.core.layout.porto import porto
from silva.core.layout.porto.interfaces import IPorto
from silva.core.views import views as silvaviews


class INewTheme(IPorto):
    """Layer for the theme.
    """
    silvaconf.resource('style.css')


class INewThemeSkin(INewTheme, ISilvaSkin):
    """Skin for the new theme.
    """
    silvaconf.skin("New theme")


silvaconf.layer(INewTheme)


class Layout(porto.Layout):
    """Skins should have a Layout class
    """


class AwesomeView(silvaviews.Page):
    """A view
    """
    silvaconf.name('awesome.html')

    def render(self):
        return u"Hello awesome!"
