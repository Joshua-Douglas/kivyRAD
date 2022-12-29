from pathlib import Path

from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.lang import Builder

kv_filepath = Path(__file__).with_suffix('.kv')
Builder.load_file(str(kv_filepath))

class ListBoxTitleNode(TreeViewLabel):
    pass

class ListBoxEntry(TreeViewLabel):
    pass

class ListBoxTree(TreeView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.remove_node(self._root)
        overriden_root = ListBoxTitleNode(text='Title', is_open=True, level=0)
        for key, value in self.root_options.items():
            setattr(overriden_root, key, value)
        self._root = self.add_node(overriden_root, None)
        

class GroupListBox(ScrollView):

    treeview = ObjectProperty(None)
    layout = ObjectProperty(None)
    title = StringProperty("Temp Title. True Default will be empty.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_treeview, 0)

    def _init_treeview(self, dt):
        standard_kivy_group = self.treeview.add_node(TreeViewLabel(text='Standard Kivy Widgets', is_open=True))
        for i in range(100):
            self.treeview.add_node(ListBoxEntry(text='Widget'), standard_kivy_group)
            self.treeview.add_node(ListBoxEntry(text='RelativeLayout'), standard_kivy_group)
            self.treeview.add_node(ListBoxEntry(text='BoxLayout'), standard_kivy_group)
