# Package

from Products.Silva.Root import Root
from silva.core import conf as silvaconf
from silva.core.interfaces import IExtensionInstaller
from zope.interface import implements

silvaconf.extension_name("smitheme.phoenix")
silvaconf.extension_title("SMI Theme Phoenix")
silvaconf.extension_depends(["Silva"])


PHOENIX_SKIN = 'smitheme.phoenix.skin.ISMIPhoenixSkin'


class Installer(object):
    implements(IExtensionInstaller)

    def install(self, root):
        root._smi_skin = PHOENIX_SKIN

    def uninstall(self, root):
        root._smi_skin = Root._smi_skin

    def is_installed(self, root):
        return root._smi_skin == PHOENIX_SKIN


install = Installer()
