from pathlib import Path

from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.lang import Builder

from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.boxlayout import BoxLayout

kv_filepath = Path(__file__).with_suffix('.kv')
Builder.load_file(str(kv_filepath))

class ListBoxEntry(TreeViewLabel):
    pass

class ListBoxTree(TreeView):
    pass
        
class GroupListBox(BoxLayout):

    treeview = ObjectProperty(None)
    layout = ObjectProperty(None)
    title = StringProperty("Temp Title. True Default will be empty.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_treeview, 0)

    def _init_treeview(self, dt):
        standard_kivy_group = self.treeview.add_node(TreeViewLabel(text='Standard Kivy Widgets', is_open=True))
        for i in range(1):
            self.treeview.add_node(ListBoxEntry(text='Widget'), standard_kivy_group)
            self.treeview.add_node(ListBoxEntry(text='RelativeLayout'), standard_kivy_group)
            self.treeview.add_node(ListBoxEntry(text='BoxLayout'), standard_kivy_group)
