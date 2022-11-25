from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserController, FileChooserLayout

Builder.load_file('kdfilechooser_style.kv', rulesonly=True)

class KDFilechooser(FileChooserController):
    _ENTRY_TEMPLATE = 'KDFileListEntry'

class KDFilechooserLayout(FileChooserLayout):
    VIEWNAME = 'list'
    _ENTRY_TEMPLATE = 'KDFileListEntry'

    def __init__(self, **kwargs):
        super(KDFilechooserLayout, self).__init__(**kwargs)
        self.fbind('on_entries_cleared', self.scroll_to_top)

    def scroll_to_top(self, *args):
        self.ids.scrollview.scroll_y = 1.0

if __name__ == '__main__':
    from kivy.app import runTouchApp
    runTouchApp(KDFilechooser())