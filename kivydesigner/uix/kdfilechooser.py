from pathlib import Path 
import os
import os.path 
import shutil
from functools import partial

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserController, FileChooserLayout
from kivy.uix.treeview import TreeView, TreeViewNode
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import FocusBehavior
from kivy.core.text import DEFAULT_FONT
from kivy.properties import BooleanProperty, StringProperty, ListProperty

from resources import get_png_resource
from modalmsg import ModalMsg

'''
The file chooser has the following structure. Defined in py and kvlang.

KDFilechooser:
  KDFilechooserLayout:
    BoxLayout:
        IconButtons:
        KDFileTreeView:
            KDFileChooserEntries:

The KDFileChooser is responsible generating and filtering the available files. Files
are searched for each time a directory is opened, so it handles node expansions. 

The KDFileChooserLayout species the layout of the file entries. This implementation 
has a header with icon buttons and a treeview used to view the directory structure. 

The KDFileTreeView is a stylized TreeView that is capable of directing focus to the 
selected node, if the node is in edit mode. 

The KDFileChooserEntries node are capable of displaying files and directores. Both node
types support two modes - read only mode and edit mode. While in edit mode the user can 
rename the file or directory. Users can cancel edits by pressing escape. 
'''

Builder.load_file('kdfilechooser.kv', rulesonly=True)

class KDFileTreeView(FocusBehavior, TreeView):

    def on_touch_down(self, touch):
        '''
        Get focus on valid touches. Nodes are selected and toggled
        at each click. super() is purposefully not called because 
        the node expansion behavior was changed. 
        '''
        if not self.collide_point(*touch.pos):
            return
        if (not self.disabled and self.is_focusable and
            ('button' not in touch.profile or
             not touch.button.startswith('scroll'))):
            self.focus = True
            FocusBehavior.ignored_touch.append(touch)

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

    def get_focus_next(self):
        #Only one child is focusable, so no need to do a full search.
        return self.selected_node.get_focus_widget()

    def get_focus_previous(self):
        return self

    def keyboard_on_key_up(self, window, keycode):
        '''
        Define the treeview-specific keybinds. Note: The nodes have a richer
        suite of keybinds while in edit mode (cntr+A, cntr+C, etc.)
        '''
        if (keycode[1] == 'f2') and self.selected_node:
            self.selected_node.bind(in_edit_mode=self.on_edit_mode_selected_node)
            self.selected_node.enable_edit_mode()
            return True
        elif (keycode[1] == 'delete' and self.select_node):
            self.delete_file_node(self.selected_node)
            return True
        return super().keyboard_on_key_up(window, keycode)

    def on_edit_mode_selected_node(self, edit_field, is_child_editable):
        # Take the focus back when leaving edit mode
        self.focus = not is_child_editable

    def delete_file_node(self, node):
        '''
        Delete node from the treeview, and remove the corresponding 
        file/directory from the file system. Ask the user before proceeding
        with the deletion. 
        '''
        def _delete_internal(node_to_delete, do_remove):
            if not do_remove:
                return
            filepath = node_to_delete.path
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)
            self.remove_node(node_to_delete)

        dir_msg = '' if node.is_leaf else " and its contents"
        msg_to_user = f'Are you sure you want to delete{node.text}{dir_msg}?'
        modal_win = ModalMsg(message=msg_to_user)
        modal_win.open(lambda win, response: _delete_internal(node, response))

    def iterate_all_nodes(self, node=None):
        parent_nodes = []
        if isinstance(node, KDFilechooserEntry):
            parent_nodes.append(node)
        else:
            # By design the top note is not a KDFilechooserEntry
            # Start at the root children to iterate over all KDFilechooserEntries
            parent_nodes.extend(self.root.nodes)
        
        for parent in parent_nodes:
            for cur_node in super().iterate_all_nodes(parent):
                yield cur_node

    def iterate_open_nodes(self, node=None):
        parent_nodes = []
        if isinstance(node, KDFilechooserEntry):
            parent_nodes.append(node)
        else:
            # By design the top note is not a KDFilechooserEntry
            # Start at the root children to iterate over all KDFilechooserEntries
            parent_nodes.extend(self.root.nodes)
        
        for parent in parent_nodes:
                for cur_node in super().iterate_open_nodes(parent):
                    yield cur_node


class KDFilechooserEntry(BoxLayout, TreeViewNode):

    locked = BooleanProperty(False)
    '''Locked entries cannot be opened, and are treated as leaf nodes'''
    path = StringProperty('')
    '''Full path to the file or directory represented by the current node'''
    entries = ListProperty([])
    '''List of child entries'''
    text = StringProperty('')
    '''Node display text - set to the file or directory name.'''
    font_name = StringProperty(DEFAULT_FONT)
    '''Node display font.'''
    in_edit_mode = BooleanProperty(False) # MAKE THIS READ ONLY
    '''Read only properly, set to True if the node text is editable. While in edit
    mode the entry displays an editable TextInput widget. Only the selected node 
    is able to be edited, so only one node can be edited at a time.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._set_text_viewer(False)

    def on_text(self, instance, new_text):
        self._text_viewer.text = new_text

    def on_touch_down(self, touch):
        if self.in_edit_mode:
            self._text_viewer.on_touch_down(touch)

    def on_is_selected(self, instance, is_sel):
        # Disable edit mode if the node is de-selected
        if self.in_edit_mode and (not is_sel):
            self.disable_edit_mode()

    def disable_edit_mode(self):
        self._set_text_viewer(False)

    def enable_edit_mode(self):
        self._set_text_viewer(True)

    def get_focus_widget(self):
        '''Return the focusable widget. Return None if the node is in read only mode.'''
        if self.in_edit_mode:
            return self._text_viewer
        return None

    def on_width(self, instance, new_width):
        self._text_viewer.text_size = new_width, None

    def on_font_name(self, *args):
        self._text_viewer.font_name = self.font_name

    def _set_text_viewer(self, edit_mode):
        # Add code to handle text input value here. 
        self.clear_widgets()
        # Only one editable node is allowed at a time. 
        # The node must be selected to enter edit mode
        if edit_mode and self.is_selected:
            # Transparent background, white text, white cursor,
            # and transparent blue selection
            edit_field = TextInput(text=self.text,
              multiline=False, focus=False, padding=[0,0], 
              halign='left', background_color=[0,0,0,0], 
              foreground_color=[1,1,1,1],
              selection_color=(0.196, 0.592, 0.992, 0.4),
              cursor_color=[1,1,1,1])

            # Focus needs to change to fire OnFocus event
            edit_field.focus = True

            # Force a center vertical alignment
            vertical_padding = (self.height - edit_field.minimum_height) // 2
            edit_field.padding = [0, max(vertical_padding, 0)]

            file_ext = Path(self.text).suffix
            if file_ext:
                selection_idx = self.text.find(file_ext)
            else:
                selection_idx = len(self.text)
            edit_field.select_text(0, selection_idx)

            def _set_cursor(edit, col, dt):
                edit.cursor = [col, 0]
            Clock.schedule_once(partial(_set_cursor, edit_field, selection_idx), 0)

            edit_field.bind(on_text_validate=self.on_text_validate)
            edit_field.bind(focus=self.on_focus)

            self._text_viewer = edit_field
            self.in_edit_mode = True
        else:
            self._text_viewer = Label(text=self.text, 
              text_size=(self.width, None), shorten=True, halign='left')
            self.in_edit_mode = False
            
        self.add_widget(self._text_viewer)

    def on_text_validate(self, edit_field):
        '''
        Fired when the TextInput is exited without cancelling the change
        (i.e. without pressing 'escape')
        '''
        original_directory = os.path.dirname(self.path) 
        new_path = os.path.join(original_directory, edit_field.text)
        try:
            os.rename(self.path, new_path)
            self.path = new_path 
            self.text = edit_field.text
        except:
            # Allow the rename to silently fail. 
            # In the future we might display the error as a popup label
            pass 

    def on_focus(self, edit_field, is_focused):
        '''
        Fired each time the TextInput is exited. Only one node is allowed
        to be editable at a time, so return to read only mode if is_focus=False.
        '''
        self._set_text_viewer(is_focused)
    
    def get_entry_icon_path(self, is_dir, is_open, icon_height, filepath):
        '''
        Set the images within the entry. Directories have error icons 
        and files have filetype logos if they are suppored by the kivydesign app.
        '''
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
    '''_ENTRY_TEMPLATE is used to create the individual entires using
    the context outlined in the comment for KDFilechooserEntryTemplate.'''

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
    '''The top label's display text.'''

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
        # Updating the treeview will clear and re-add the nodes
        # The new nodes will not have remember the open state
        # Cache here, and reapply after re-adding if still present
        self._open_node_cache.clear()
        for node in treev.iterate_open_nodes():
            # Might look like a weird check, but iterate_open_nodes iterates over
            # all nodes except for those who have a closed parent. Therefore it 
            # does returned closed nodes and leaf nodes.
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
        for node in treev.iterate_all_nodes():
            if node.path == self.controller.selection[0]:
                return node
        
    def new_file(self):
        '''
        Add a new file, in the same directory as the currently selected
        node. Place the file in the root directory if no file is selected. 

        The newly added file will start in edit mode. 
        '''
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

        new_filename = 'new_file'
        new_path = os.path.join(new_dirname, new_filename)
        i = 1
        while os.path.exists(new_path):
            i += 1
            new_filename = f'new_file{i}'
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
        new_entry.enable_edit_mode()
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