# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.ExtensionRegistry import extensionRegistry
from silva.core.conf.installer import DefaultInstaller
from silva.core.upgrade import localsite
import zope.interface


class IExtension(zope.interface.Interface):
    """silva.core.layout extension.
    """

class CoreLayoutInstaller(DefaultInstaller):
    __name__ = "silva.core.layout.install"


    def install_custom(self, root):
        if hasattr(root, 'preview_html'):
            root.manage_delObjects(['preview_html',])
        root.manage_delObjects(['standard_error_message',])
        factory = root.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('standard_error_message')
        sem = getattr(root, 'standard_error_message')
        sem.write("""##parameters=error_type,error_value,error_traceback,error_tb,error_message,error_log_url
from silva.core.layout.compat import standard_error_message

return standard_error_message(context, context.REQUEST, error_value)
""")
        localsite.activate(root)



install = CoreLayoutInstaller('Silva Core Layout', IExtension)


def initialize(context):
    import markers

    extensionRegistry.register(
        'Silva Core Layout', 'Silva 2.2 Layout system compatiblity',
        context, [], install, depends_on=('Silva', 'SilvaLayout',),)
    context.registerClass(
        markers.CustomizationMarker,
        constructors = (markers.manage_addCustomizationMarkerForm,
                        markers.manage_addCustomizationMarker),
        icon="markers.png",
        )
