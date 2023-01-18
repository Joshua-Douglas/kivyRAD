from pathlib import Path

from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

kv_filepath = Path(__file__).with_suffix('.kv')
Builder.load_file(str(kv_filepath))

class ListBoxNode(TreeViewLabel):
    is_focused = BooleanProperty(False)
    '''
    A node is focused if it was the most recently selected node. 
    A node can be selected but unfocused, if a different node 
    that does not support selection was clicked by the user.
    '''

class ListBoxGroup(ListBoxNode):
    pass

class ListBoxEntry(ListBoxNode):
    pass

class ListBoxTree(TreeView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._focused_node = None
    
    def select_node(self, node):
        if self._focused_node:
            self._focused_node.is_focused = False
        node.is_focused = True
        self._focused_node = node
        super().select_node(node)

class GroupListBox(BoxLayout):

    treeview = ObjectProperty(None)
    layout = ObjectProperty(None)
    title = StringProperty("")

    def add_group(self, group_name, items):
        group = self.treeview.add_node(ListBoxGroup(text=group_name, is_open=True))
        for item in sorted(items):
            self.treeview.add_node(ListBoxEntry(text=item), group)

    def clear(self):
        all_nodes = tuple(self.treeview.iterate_all_nodes())
        for node in all_nodes:
            self.treeview.remove_node(node)