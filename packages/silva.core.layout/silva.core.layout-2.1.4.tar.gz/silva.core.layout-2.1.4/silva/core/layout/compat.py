# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# This file contains compatibility code to behave like in Silva
# 2.2. In Silva 2.2 that code is directly on SilvaObject. Here you
# have to update the standard_error_message in ZMI to call it.

from AccessControl import ModuleSecurityInfo, allow_module
from silva.core.layout.utils import queryMultiAdapterWithInterface
from silva.core.views.interfaces import IHTTPResponseHeaders
from zope.interface import providedBy
from zope.component import queryMultiAdapter

allow_module('silva.core.layout.compat')
module_security = ModuleSecurityInfo('silva.core.layout.compat')

module_security.declarePublic('standard_error_message')
# Query for an error page. We redefine it to have a correct object as
# context, and not an interface ... which does not make code really
# reusable.
def standard_error_message(context, request, error):
    header_handler = queryMultiAdapter(
        (error, request), IHTTPResponseHeaders)
    if header_handler: header_handler()

    if request.method == 'HEAD':
        return ''

    if error:
        page = queryMultiAdapterWithInterface(
            (providedBy(error), request,), context, name='error.html')
        if page is not None:
            return page.__of__(context)()
    return u"<p>I am sorry, but it sounds like there is an error.</p>"

