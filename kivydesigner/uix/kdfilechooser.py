from pathlib import Path

from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserController, FileChooserLayout
from kivy.uix.treeview import TreeViewNode
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, StringProperty, ListProperty

from resources import get_png_resource

Builder.load_file('kdfilechooser_style.kv', rulesonly=True)

class KDFilechooserEntry(BoxLayout, TreeViewNode):

    locked = BooleanProperty(False)
    '''Locked entries cannot be opened, and are treated as leaf nodes'''
    path = StringProperty('')
    entries = ListProperty([])
    
    def get_entry_icon_path(self, is_dir, is_open, icon_height, filepath):
        if is_dir:
            suffix = 'opened' if is_open else 'closed'
            return f'atlas://data/images/defaulttheme/tree_{suffix}'
        else:
            ext = Path(filepath).suffix
            if ext == '.py':
                icon_name = 'python-icon'
            elif ext == '.kv':
                icon_name = 'kivy-icon'
            else:
                # Add gentle icon here for unsupported file
                icon_name = ''
            return get_png_resource(icon_name, icon_height)

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