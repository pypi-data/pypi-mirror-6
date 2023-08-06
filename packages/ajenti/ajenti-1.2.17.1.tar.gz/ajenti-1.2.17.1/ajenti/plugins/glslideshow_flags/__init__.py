from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Screensaver Prefs',
    icon='picture',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import glslideshow_flags

