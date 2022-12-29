from pathlib import Path

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.lang import Builder

kv_filepath = Path(__file__).with_suffix('.kv')
Builder.load_file(str(kv_filepath))

class GroupListBox(ScrollView):

    treeview = ObjectProperty(None)
    layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_treeview, 0)

    def _init_treeview(self, dt):
        standard_kivy_group = self.treeview.add_node(TreeViewLabel(text='Standard Kivy Widgets'))
        for i in range(100):
            self.treeview.add_node(TreeViewLabel(text='Widget'), standard_kivy_group)
            self.treeview.add_node(TreeViewLabel(text='RelativeLayout'), standard_kivy_group)
            self.treeview.add_node(TreeViewLabel(text='BoxLayout'), standard_kivy_group)
