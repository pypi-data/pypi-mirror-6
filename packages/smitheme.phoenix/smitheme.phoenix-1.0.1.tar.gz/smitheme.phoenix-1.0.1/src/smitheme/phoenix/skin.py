from five import grok
from silva.core.smi.interfaces import ISMILayer
from silva.core import conf as silvaconf
from silva.core.smi import preview
from silva.core.smi.smi import SMIFavicon


class ISMIPhoenixLayer(ISMILayer):
    pass


class ISMIPhoenixSkin(ISMIPhoenixLayer):
    silvaconf.resource('reset.css')
    silvaconf.resource('phoenix.css')


class PreviewFrameset(preview.PreviewFrameset):
    grok.layer(ISMIPhoenixLayer)
    rows = '101px,*'


class Favicon(SMIFavicon):
    grok.layer(ISMIPhoenixLayer)

    @property
    def favicon_url(self):
        return self.static['silva.ico']
