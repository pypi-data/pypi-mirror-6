
from Products.Silva.Root import Root
from silva.core import conf as silvaconf
from silva.core.interfaces import IExtensionInstaller
from zope.interface import implements

silvaconf.extension_name("smitheme.industrial")
silvaconf.extension_title("SMI Theme Industrial")
silvaconf.extension_depends(["Silva"])


SKIN = 'smitheme.industrial.skin.ISMIIndustrialSkin'


class Installer(object):
    implements(IExtensionInstaller)

    def install(self, root, extension):
        root._smi_skin = SKIN

    def uninstall(self, root, extension):
        root._smi_skin = Root._smi_skin

    def is_installed(self, root, extension):
        return root._smi_skin == SKIN


install = Installer()
