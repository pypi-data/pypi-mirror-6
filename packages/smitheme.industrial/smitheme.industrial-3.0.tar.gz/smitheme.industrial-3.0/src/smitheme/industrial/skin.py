
from megrok.pagetemplate import PageTemplate
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from silva.core import conf as silvaconf
from silva.ui.smi import SMI
from five import grok
from js import jqueryui


class ISMIIndustrialSkin(IDefaultBrowserLayer):
    silvaconf.resource(jqueryui.smoothness)
    silvaconf.resource('css/style.css')
    silvaconf.resource('css/smi.css')
    silvaconf.resource('css/jstree.css')
    silvaconf.resource('css/navigation.css')
    silvaconf.resource('css/actions.css')
    silvaconf.resource('css/forms.css')
    silvaconf.resource('css/formwidgets.css')
    silvaconf.resource('css/listing.css')


# Customize SMI template
# class SMITemplate(PageTemplate):
#     grok.view(SMI)
#     grok.layer(ISMIIndustrialSkin)

