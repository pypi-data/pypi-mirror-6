# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""
    Grok the skin:
    >>> grok('silva.core.layout.tests.grok.porto_fixtures')

    >>> from zope.interface import alsoProvides
    >>> from zope.component import getMultiAdapter
    >>> from Products.Silva.testing import TestRequest
    >>> from silva.core.layout.tests.grok.porto_fixtures.skin import INewTheme

    Initialize a test request and get some content
    >>> request = TestRequest()
    >>> content = getRootFolder()

    The skin is not registered on the request the adapter lookup should fail
    >>> getMultiAdapter((content, request), name="awesome.html")
    Traceback (most recent call last):
        ...
    ComponentLookupError:...

    We register the layer on the request:
    >>> alsoProvides(request, INewTheme)

    We now ask for the view. We should get our layout:
    >>> view = getMultiAdapter((content, request), name="awesome.html")
    >>> view
    <silva.core.layout.tests.grok.porto_fixtures.skin.AwesomeView object at ...>

    >>> 'Hello awesome!' in view()
    True

    >>> view.layout
    <silva.core.layout.porto.porto.MainLayout object at ...>


"""
