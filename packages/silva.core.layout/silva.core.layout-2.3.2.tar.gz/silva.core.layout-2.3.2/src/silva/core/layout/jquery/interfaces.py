# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core import conf as silvaconf
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IJQueryResources(IDefaultBrowserLayer):
    silvaconf.resource('jquery-1.4.4.js')


class IJQueryUIResources(IJQueryResources):
    silvaconf.resource('jquery-ui-1.8.4.custom.min.js')
    silvaconf.resource('jquery-ui-i18n.js')
    silvaconf.resource('jquery-ui-1.8.4.custom.css')
