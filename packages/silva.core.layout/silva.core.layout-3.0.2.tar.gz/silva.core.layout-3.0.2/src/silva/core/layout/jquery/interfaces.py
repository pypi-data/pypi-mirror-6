# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core import conf as silvaconf
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from js import jquery, jqueryui


class IJQueryResources(IDefaultBrowserLayer):
    silvaconf.resource(jquery.jquery)


# XXX i18n is not included in jqueryui silvaconf.resource('jquery-ui-i18n.js')
class IJQueryUIResources(IJQueryResources):
    silvaconf.resource(jqueryui.jqueryui)
    silvaconf.resource(jqueryui.smoothness)
