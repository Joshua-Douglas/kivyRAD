from pathlib import Path 
import os.path 

from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserController, FileChooserLayout
from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty, StringProperty, ListProperty

from resources import get_png_resource

Builder.load_file('kdfilechooser_style.kv', rulesonly=True)

class KDFileTreeView(TreeView):

    def on_touch_down(self, touch):
        node = self.get_node_at_pos(touch.pos)
        if not node:
            return
        if node.disabled:
            return
        # Toggle and select the node at each selection
        self.toggle_node(node)
        self.select_node(node)
        node.dispatch('on_touch_down', touch)
        return True

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
                icon_name = 'default-file'
            return get_png_resource(icon_name, icon_height)

class KDFilechooser(FileChooserController):
    _ENTRY_TEMPLATE = 'KDFilechooserEntryTemplate'

    def entry_touched(self, entry, touch):
        '''
        Update selections. Override parent implementation to 
        prevent entries from opening. KDTreeView was modified so 
        entries will now expand instead. 
        '''
        if ('button' in touch.profile and touch.button in (
                'scrollup', 'scrolldown', 'scrollleft', 'scrollright')):
            return False

        _dir = self.file_system.is_dir(entry.path)
        dirselect = self.dirselect

        if _dir and dirselect and touch.is_double_tap:
            return

        if self.multiselect:
            if entry.path in self.selection:
                self.selection.remove(entry.path)
            else:
                if _dir and not self.dirselect:
                    return
                self.selection.append(entry.path)
        else:
            if _dir and not self.dirselect:
                return
            self.selection = [os.path.abspath(os.path.join(self.path, entry.path)), ]

    def entry_released(self, entry, touch):
        '''
        Dispatch double click submission. Override parent implementation to 
        prevent entries from opening. KDTreeView was modified so 
        entries will now expand instead. 
        '''
        if ('button' in touch.profile and touch.button in (
              'scrollup', 'scrolldown', 'scrollleft', 'scrollright')):
            return False
        if not self.multiselect:
            if self.file_system.is_dir(entry.path) and not self.dirselect:
                return
            elif touch.is_double_tap:
                if self.dirselect and self.file_system.is_dir(entry.path):
                    return
                else:
                    self.dispatch('on_submit', self.selection, touch)

class KDFilechooserLayout(FileChooserLayout):
    VIEWNAME = 'list'
    _ENTRY_TEMPLATE = 'KDFilechooserEntryTemplate'

    title = StringProperty('')

    def __init__(self, **kwargs):
        super(KDFilechooserLayout, self).__init__(**kwargs)
        self.fbind('on_entries_cleared', self.scroll_to_top)
        self._open_node_cache = set()

    def scroll_to_top(self, *args):
        self.ids.scrollview.scroll_y = 1.0

    def get_title_name(self, rootpath):
        if rootpath and os.path.isdir(rootpath):
            return os.path.basename(rootpath).upper()
        return 'NO FOLDER OPENED'

    def refresh_entries(self):
        '''Refresh the entries, to update with any changes to the directory.'''
        treev = self.ids.treeview
        parents = treev.root.nodes

        # Updating the treeview will clear and re-add the nodes
        # The new nodes will not have remember the open state
        # Cache here, and reapply after re-adding if still present
        self._open_node_cache.clear()
        for parent in parents:
            for node in treev.iterate_open_nodes(parent):
                if node.is_open:
                    self._open_node_cache.add(node.path)

        self.controller._trigger_update()

    def on_entry_added(self, node, parent): 
        treev = self.ids.treeview
        treev.add_node(node)

        if node.path in self._open_node_cache:
            # Restore node & child open state, if necessary
            for child in treev.iterate_all_nodes(node):
                if child.path in self._open_node_cache:
                    treev.toggle_node(child)
                    self._open_node_cache.remove(child.path)


if __name__ == '__main__':
    from kivy.app import runTouchApp
    from pathlib import Path
    from kivy.factory import Factory
    Factory.register('IconButton', module='iconbutton')

    rootdir = Path(__file__).parent.parent.parent
    runTouchApp(KDFilechooser(rootpath=str(rootdir)))