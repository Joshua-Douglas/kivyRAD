from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserController, FileChooserLayout
from kivy.uix.treeview import TreeViewNode
from kivy.uix.boxlayout import BoxLayout

Builder.load_file('kdfilechooser_style.kv', rulesonly=True)

class KDFilechooserEntry(BoxLayout, TreeViewNode):
    
    def get_entry_icon_path(self, is_dir, is_open):
        if is_dir:
            suffix = 'opened' if is_open else 'closed'
            return f'atlas://data/images/defaulttheme/tree_{suffix}'
        else:
            return "C:\\Users\\joshu\\source\\repos\\kivydesigner\\kivydesigner\\data\\kivy-icon-32.png"

class KDFilechooser(FileChooserController):
    _ENTRY_TEMPLATE = 'KDFilechooserEntryTemplate'

class KDFilechooserLayout(FileChooserLayout):
    VIEWNAME = 'list'
    _ENTRY_TEMPLATE = 'KDFilechooserEntryTemplate'

    def __init__(self, **kwargs):
        super(KDFilechooserLayout, self).__init__(**kwargs)
        self.fbind('on_entries_cleared', self.scroll_to_top)

    def scroll_to_top(self, *args):
        self.ids.scrollview.scroll_y = 1.0

if __name__ == '__main__':
    from kivy.app import runTouchApp
    from pathlib import Path

    rootdir = Path(__file__).parent.parent
    runTouchApp(KDFilechooser(rootpath=str(rootdir)))