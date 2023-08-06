from ajenti.api import *
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder


@plugin
class GLSlideShowPrefs (SectionPlugin):
    default_classconfig = {
        'option_1_enable': True # etc
    }
    classconfig_root = True

    def init(self):
        self.title = _('Screensaver Prefs')
        self.icon = 'picture'
        self.category = _('Sanickiosk')

        self.append(self.ui.inflate('glslideshow_flags:main'))
        self.binder = Binder(self, self)
        self.binder.populate()

    @on('save', 'click')
    def save(self):
        self.binder.update()
        self.save_classconfig()

        cmdline = ''
        print self.classconfig
        for option in ['option_1', 'option_2']:
            if self.classconfig.get(option + '_enable', False):
                cmdline += '--%s ' % option
                value = self.classconfig.get(option + '_value', False)
                if value:
                    cmdline += '%s ' % value

        print cmdline # save
