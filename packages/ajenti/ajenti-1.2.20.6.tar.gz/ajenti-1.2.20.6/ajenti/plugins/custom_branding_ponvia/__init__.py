from ajenti.api import *
from ajenti.plugins import *

info = PluginInfo(
    title='Branding',
    icon='asterisk',
    dependencies=[
        PluginDependency('configurator'),
    ]
)

#raise Exception()

# -------------------------------------------------------------------------------------------------
# Hide licensing UI

try:
    import ajenti.licensing
    ajenti.licensing.Licensing.licensing_active = False
except:
    pass


# -------------------------------------------------------------------------------------------------
# Patch the Configure section

from ajenti.plugins.configurator.configurator import Configurator

old_init = Configurator.init


def new_init(self, *args):
    old_init(self, *args)

    # patch the label
    lbl = self.nearest(lambda x: x.typeid == 'label' and x.style == 'small')[0]
    lbl.text = 'Custom text'

    # or just hide it completely
    # self.nearest(lambda x: x.typeid == 'formgroup' and x.text == _('Other'))[0].delete()

Configurator.init = new_init
