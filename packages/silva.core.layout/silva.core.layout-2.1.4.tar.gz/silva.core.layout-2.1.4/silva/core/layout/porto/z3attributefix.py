# Fixes for the z3attributes 'edit' object on 2.1. On 2.2 this thing
# is in the SMILayout, so no error there.

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.Silva.SilvaObject import Zope3ViewAttribute

from silva.core.views import views as silvaviews
from five import grok


grok.layer(IDefaultBrowserLayer)


class MainLayout(silvaviews.Layout):
    """Add a simple layout to render correctly errors in SMI/half SMI.
    This should be only needed for Silva 2.1 using silva.core.layout.
    """
    grok.template('mainlayout')
    grok.context(Zope3ViewAttribute)

