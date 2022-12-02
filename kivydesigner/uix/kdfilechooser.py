from pathlib import Path 
import os.path 

from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserController, FileChooserLayout
from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import FocusBehavior
from kivy.core.text import DEFAULT_FONT
from kivy.properties import BooleanProperty, StringProperty, ListProperty

from resources import get_png_resource

Builder.load_file('kdfilechooser_style.kv', rulesonly=True)

class KDFileTreeView(FocusBehavior, TreeView):

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
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

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        super().keyboard_on_key_down(window, keycode, text, modifiers)
        if self.focus and self.selected_node:
            self.selected_node.on_key_down(window, keycode, text, modifiers)

    def keyboard_on_key_up(self, window, keycode):
        if (keycode[1] == 'f2') and self.selected_node:
            #self.focus_next = self.selected_node
            #self.focus = False
            self.selected_node.enable_edit_mode()
            #self.focus_next = self.selected_node._text_viewer
            # Give focus to selected node
            return True
        return super().keyboard_on_key_up(window, keycode)

class KDFilechooserEntry(BoxLayout, TreeViewNode):

    locked = BooleanProperty(False)
    '''Locked entries cannot be opened, and are treated as leaf nodes'''
    path = StringProperty('')
    entries = ListProperty([])
    text = StringProperty('')
    font_name = StringProperty(DEFAULT_FONT)
    readonly = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_text_viewer(False)

    def on_text(self, *args):
        self._text_viewer.text = self.text

    def on_key_down(self, window, keycode, text, modifiers):
        if self._in_edit_mode():
            # Doesn't handle delete or special commands. Need to wire up this functionality as well.
            self._text_viewer.keyboard_on_textinput(window, text)
            return True
        return False

    def on_is_selected(self, *args):
        # Disable edit mode if the node is de-selected
        if self._in_edit_mode() and (not self.is_selected):
            self.disable_edit_mode()

    def disable_edit_mode(self):
        self._set_text_viewer(False)

    def enable_edit_mode(self):
        self._set_text_viewer(True)

    def _in_edit_mode(self):
        return isinstance(self._text_viewer, TextInput)

    def on_width(self, *args):
        self._text_viewer.text_size = self.width, None

    def on_font_name(self, *args):
        self._text_viewer.font_name = self.font_name

    def _set_text_viewer(self, edit_mode):
        # Add code to handle text input value here. 
        self.clear_widgets()
        # Only one editable node is allowed at a time. 
        # The node must be selected to enter edit mode
        if edit_mode and self.is_selected:
            self._text_viewer = TextInput(text=self.text,
              multiline=False, focus=True)
        else:
            self._text_viewer = Label(text=self.text, 
              text_size=(self.width, None), shorten=True, halign='left')
            
        self.add_widget(self._text_viewer)
    
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
        super().__init__(**kwargs)
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
        treev.add_node(node, parent)

        if node.path in self._open_node_cache:
            # Restore node & child open state, if necessary
            for child in treev.iterate_all_nodes(node):
                if child.path in self._open_node_cache:
                    treev.toggle_node(child)
                    self._open_node_cache.remove(child.path)

    def collapse_all_nodes(self):
        treev = self.ids.treeview
        for root_node in treev.root.nodes:
            if root_node.is_open:
                treev.toggle_node(root_node)

    def get_selected_node(self):
        '''Return the first selected node.'''
        if len(self.controller.selection) == 0:
            return None 

        treev = self.ids.treeview
        parents = treev.root.nodes
        for parent in parents:
            for child in treev.iterate_all_nodes(parent):
                if child.path == self.controller.selection[0]:
                    return child
        
    def new_file(self):
        cur_selection = self.get_selected_node()
        if cur_selection:
            if (not cur_selection.is_leaf) and cur_selection.is_open:
                new_parent = cur_selection
                new_dirname = cur_selection.path
            else:
                new_parent = cur_selection.parent_node 
                new_dirname = os.path.dirname(cur_selection.path)
        else:
            new_parent = self.ids.treeview.root
            new_dirname = self.controller.rootpath

        new_filename = 'new_file.kv'
        new_path = os.path.join(new_dirname, new_filename)
        i = 1
        while os.path.exists(new_path):
            i += 1
            new_filename = f'new_file{i}.kv'
            new_path = os.path.join(new_dirname, new_filename)

        open(new_path, 'x')
        ctx = {'name': new_filename,
               'get_nice_size': None,
               'path': new_path,
               # Template expects callable controller
               'controller': lambda: self.controller,
               'isdir': False,
               'parent': new_parent,
               'sep': os.path.sep}

        new_entry = self.controller._create_entry_widget(ctx)
        self.ids.treeview.select_node(new_entry)
        self.controller.dispatch('on_entry_added', new_entry, new_parent)
        self.controller.files.append(new_path)
        self.controller.selection = [new_path,]

if __name__ == '__main__':
    from kivy.app import runTouchApp
    from pathlib import Path
    from kivy.factory import Factory
    Factory.register('IconButton', module='iconbutton')

    rootdir = Path(__file__).parent.parent.parent
    runTouchApp(KDFilechooser(rootpath=str(rootdir)))