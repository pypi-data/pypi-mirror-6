# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from OFS.Folder import Folder

from five import grok
from grokcore.view.interfaces import ITemplate as IGrokTemplate
from infrae.layout.interfaces import IPage
from zope.component import getGlobalSiteManager, queryAdapter
from zope.component import getUtility, getUtilitiesFor
from zope.configuration.name import resolve as pythonResolve
from zope.interface.interfaces import IInterface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.layout import interfaces
from silva.core.layout.interfaces import ICustomizable, ICustomizableType
from silva.core.layout.interfaces import ICustomizableMarker, ILayerType
from silva.core.layout.utils import findSite, findNextSite, queryAdapterOnClass
from silva.core.services.base import SilvaService
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IContentProvider, IViewlet
from silva.core.views.interfaces import ICustomizedTemplate
from silva.core.views.interfaces import ITemplateNotCustomizable
from silva.core.views.ttwtemplates import TTWViewTemplate


def identifier(obj):
    """Gives the Python identifier for the given object, so after we
    can do resolve on it to get it back.
    """
    if IInterface.providedBy(obj):
        return obj.__identifier__
    return obj.__name__


def resolve(name):
    """Resolve the name.
    """
    obj = pythonResolve(name)
    if not IInterface.providedBy(obj):
        return obj.__provides__._implements
    return obj


class ViewManager(grok.Adapter):

    grok.implements(interfaces.IViewManager)
    grok.adapts(ISilvaObject)

    def sites(self):
        """Gives a list of local sites.
        """
        site = findNextSite(self.context)
        while not (site is None):
            yield (site.getSiteManager(), u'/'.join(site.getPhysicalPath()))
            site = findNextSite(site)
        yield (getGlobalSiteManager(), None)


    def _entry(self, reg, sitename):
        """Build a ViewInfo from the registration info.
        """
        if ITemplateNotCustomizable.implementedBy(reg.factory):
            return None
        entry = queryAdapterOnClass(reg.factory, interfaces.IViewInfo)
        if entry is None:
            entry = queryAdapter(reg.factory, interfaces.IViewInfo)
            if entry is None:
                if isAFiveTemplate(reg.factory):
                    entry = FiveViewInfo(reg.factory)

        if not (entry is None):
            entry.origin = sitename
            entry.registration = reg

        return entry

    def search(self, interface, layer, sort=False):
        """Search and return all ViewInfo object for customizable
        views for interface in layer layer.
        """

        def viewsFor(site, sitename):
            for reg in site.registeredAdapters():
                if (len(reg.required) >= 2 and
                    interface.isOrExtends(reg.required[0]) and
                    reg.required[0].isOrExtends(ICustomizable) and
                    reg.required[1].isOrExtends(layer)):

                    entry = self._entry(reg, sitename)
                    if entry:
                        yield entry

        views = []
        for site in self.sites():
            views.extend(viewsFor(*site))

        if sort is True:
            views = sorted(views, key=lambda e: e.name)

        result = []
        for view in views:
            result.append({'view': view,
                           'signature': self.get_signature(view),})
        return result

    def get(self, type_, name, origin, required):
        """Retrieve the ViewInfo which correspond to the given settings.
        """
        for site, sitename in self.sites():
            if sitename != origin:
                continue
            for reg in site.registeredAdapters():
                if (reg.required == required and
                    reg.name == name and
                    reg.provided == type_):
                    return self._entry(reg, sitename)
            return None
        return None

    def from_signature(self, signature):
        signature = signature.split(':')
        type_ = resolve(signature[0])
        name = signature[1]
        origin = signature[2] != 'None' and signature[2] or None
        required = tuple(map(resolve, signature[3:]))
        return self.get(type_, name, origin, required)

    def get_signature(self, view_entry):
        required = ':'.join(map(lambda x: identifier(x),
                                view_entry.registration.required))
        return '%s:%s:%s:%s' % (identifier(view_entry.registration.provided),
                                view_entry.registration.name,
                                view_entry.origin,
                                required)


class DefaultViewInfo(grok.Adapter):
    """Default base class for view entries.
    """

    grok.implements(interfaces.IViewInfo)
    grok.baseclass()

    type_ = u'Five Page Template'
    template = None
    config = None
    origin = None

    registration = None

    @property
    def name(self):
        return self.registration.name

    @property
    def for_(self):
        return identifier(self.registration.required[0])

    @property
    def layer(self):
        return identifier(self.registration.required[1])

    @property
    def code(self):
        if self.template:
            return open(self.template, 'rb').read()
        return u''

    def generateId(self):
        tid = '-'.join(map(lambda r: identifier(r).split('.')[-1],
                           self.registration.required))
        return '%s-%s' % (tid, self.name)

    def permission(self):
        permissions = self.context.__ac_permissions__
        for permission, methods in permissions:
            if methods[0] in ('', '__call__',):
                return permission
        return None

    def _view(self):
        # Return the view class to use:
        return self.context.__bases__[0]

    def customize(self, where, customized_for=None, customized_layer=None):

        if customized_for is None:
            customized_for = self.registration.required[0]
        if customized_layer is None:
            customized_layer = self.registration.required[1]

        template_id = str(self.generateId())
        viewclass = self._view()

        if ITemplateNotCustomizable.implementedBy(viewclass):
            raise ValueError, "This view don't want to be customized."

        permission = self.permission()
        service = getUtility(interfaces.ICustomizationService)
        site = findSite(service)

        if ICustomizedTemplate.providedBy(self.context):
            if self.origin == u'/'.join(site.getPhysicalPath()):
                raise ValueError(
                    u"This template have been already customized "
                    u"in the same directory.")

        new_template = TTWViewTemplate(template_id, self.code,
                                       view=viewclass, permission=permission)

        service._setObject(template_id, new_template)
        new_template = getattr(service, template_id)

        required = list(self.registration.required)
        required[0] = customized_for
        required[1] = customized_layer

        manager = site.getSiteManager()
        manager.registerAdapter(new_template,
                                required=tuple(required),
                                provided=self.registration.provided,
                                name=self.registration.name)
        return new_template


class GrokViewInfo(DefaultViewInfo):
    """A Grok View.
    """

    grok.context(IPage)

    type_ = u'Grok Page Template'

    @property
    def template(self):
        if (hasattr(self.context, 'template') and
            self.context.template is not None):
            if IGrokTemplate.providedBy(self.context.template):
                return self.context.template._template.filename
        return None

    def generateId(self):
        return 'grok-template-%s' % super(GrokViewInfo, self).generateId()


class GrokContentProviderEntry(GrokViewInfo):
    """A Grok Content Provider.
    """

    grok.context(IContentProvider)

    type_ = u'Grok Content Provider'

    def permission(self):
        return None

    def generateId(self):
        return 'grok-contentprovider-%s' % super(GrokViewInfo, self).generateId()


class GrokViewletEntry(GrokViewInfo):
    """A Grok Viewlet.
    """

    grok.context(IViewlet)

    type_ = u'Grok Viewlet'

    def _view(self):
        return self.context

    def generateId(self):
        return 'grok-viewlet-%s' % super(GrokViewInfo, self).generateId()


class CustomizedViewInfo(DefaultViewInfo):
    """A Customized View.
    """

    grok.context(ICustomizedTemplate)

    type_ = u'Customized Page Template'

    @property
    def template(self):
        return self.context.id

    @property
    def code(self):
        return self.context.read()

    def generateId(self):
        return 'customized-%s' % super(CustomizedViewInfo, self).generateId()

    def _view(self):
        return self.context.view

    def permission(self):
        return self.context.permission


class FiveViewInfo(DefaultViewInfo):
    """A regular Five template.
    """

    grok.baseclass()

    @property
    def config(self):
        return self.registration.info.file

    @property
    def template(self):
        return self.context.index.filename

    def generateId(self):
        return 'five-template-%s' % super(FiveViewInfo, self).generateId()



def isAFiveTemplate(factory):
    """There is no interfaces for Five templates. That's the hack to
    guess it's an five template.
    """
    return (hasattr(factory, '__name__') and
            factory.__name__.startswith('SimpleViewClass'))


class CustomizationService(Folder, SilvaService):
    """Customize filesystem based templates.
    """
    meta_type = 'Silva Customization Service'
    default_service_identifier = 'service_customization'
    grok.implements(interfaces.ICustomizationService)
    silvaconf.icon('customization.png')

    manage_options = (
        {'label':'Customize', 'action':'manage_customization'},
        ) + Folder.manage_options

    def availablesInterfaces(self, base=ICustomizable):
        interfaces = getUtilitiesFor(ICustomizableType, context=self)
        return sorted([name for name, interface in interfaces
                       if interface.isOrExtends(base)])

    def availablesLayers(self, base=IDefaultBrowserLayer):
        layers = getUtilitiesFor(ILayerType)
        return sorted([name for name, layer in layers
                       if layer.isOrExtends(base)])

    def availablesTemplates(self, interface, layer=IDefaultBrowserLayer):
        return interfaces.IViewManager(self).search(interface, layer, sort=True)


class CustomizationManagementView(silvaviews.ZMIView):

    grok.require('zope2.ViewManagementScreens')
    grok.baseclass()

    interface = None
    layer = None

    def availablesInterfaces(self):
        """Return available interfaces starting from base.
        """
        base = self.interface
        if base is None:
            base = ICustomizable

        return self.context.availablesInterfaces(base)

    def availablesInterfacesAndMarkers(self):
        """Return available interfaces starting from base and markers.
        """
        interfaces = self.availablesInterfaces()
        interfaces.extend(self.context.availablesInterfaces(
                ICustomizableMarker))
        return interfaces

    def availablesLayers(self):
        """Return available layers starting from base.
        """
        base = self.layer
        if base is None:
            base = IDefaultBrowserLayer

        return self.context.availablesLayers(base)


class ManageCustomTemplates(CustomizationManagementView):

    grok.name('manage_customization')

    def update(self):
        self.availableTemplates = []
        self.selectedInterface = self.request.form.get('interface', None)
        self.selectedLayer = self.request.form.get(
            'layer', IDefaultBrowserLayer.__identifier__)

        if self.selectedInterface:
            interface = getUtility(
                ICustomizableType, name=self.selectedInterface)
            layer = getUtility(ILayerType, name=self.selectedLayer)

            self.availableTemplates = self.context.availablesTemplates(
                interface, layer)
        else:
            self.selectedInterface = ISilvaObject.__identifier__


class ManageViewTemplate(CustomizationManagementView):

    silvaconf.name('manage_template')
    # Fix for grok template inherit issue
    silvaconf.template('manageviewtemplate')

    def update(self):
        assert 'signature' in self.request.form

        self.signature = self.request.form['signature']
        self.entry = interfaces.IViewManager(self.context).from_signature(
            self.signature)
        if self.entry is None:
            raise ValueError, 'Template not found'

        self.interface = self.entry.registration.required[0]
        self.layer = self.entry.registration.required[1]



class ManageCreateCustomTemplate(ManageViewTemplate):

    grok.name('manage_createCustom')

    def update(self):
        super(ManageCreateCustomTemplate, self).update()

        for_name = self.request.form['customize_for']
        layer_name = self.request.form['customize_layer']
        customize_for = getUtility(ICustomizableType, name=for_name)
        customize_layer = getUtility(ILayerType, name=layer_name)

        new_template = self.entry.customize(
            self, customize_for, customize_layer)

        self.redirect(new_template.absolute_url() + '/manage_workspace')


