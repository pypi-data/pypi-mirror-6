# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface.interface import InterfaceClass
from zope.component.interface import provideInterface

from silva.core.conf import only_for
from silva.core.layout.interfaces import ICustomizableLayer
from silva.core.layout.interfaces import ICustomizableType, ICustomizable
from silva.core.layout.interfaces import ILayerType, ISilvaSkin
from zeam.component import getSite

import martian


class InterfaceGrokker(martian.InstanceGrokker):
    """We register interfaces than people can customize as utility on
    ISilvaCustomizable.
    """
    martian.component(InterfaceClass)

    def grok(self, name, interface, module_info, config, **kw):
        if interface.extends(ICustomizable):
            # Unfortunately we can't use context on interfaces.
            specs = (only_for.bind().get(interface), )
            name = interface.__identifier__
            config.action(
                discriminator=('component', specs, ICustomizableType, name),
                callable=getSite().register,
                args=(interface, specs, ICustomizableType, name))
            return True

        if (interface.extends(ICustomizableLayer) and
            not interface.isOrExtends(ISilvaSkin)):
            config.action(
                discriminator=('utility', ILayerType, interface),
                callable=provideInterface,
                args=('', interface, ILayerType))
            return True

        return False



