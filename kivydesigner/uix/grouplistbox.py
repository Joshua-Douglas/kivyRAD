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

    def on_touch_down(self, touch):
        '''
        Modify node expansion behavior. Toggle node 
        anytime it is clicked, not just when the 
        expand/collapse icon is clicked.
        '''
        if not self.collide_point(*touch.pos):
            return

        node = self.get_node_at_pos(touch.pos)
        if (not node) or node.disabled:
            return
            
        # Toggle and select the node at each selection
        self.toggle_node(node)
        self.select_node(node)
        
        node.dispatch('on_touch_down', touch)
        return True

class GroupListBox(BoxLayout):

    treeview = ObjectProperty(None)
    layout = ObjectProperty(None)
    title = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._init_treeview, 0)

    def _init_treeview(self, dt):
        standard_kivy_group = self.treeview.add_node(ListBoxGroup(text='STANDARD KIVY WIDGETS', is_open=True))
        for i in range(10):
            self.treeview.add_node(ListBoxEntry(text='Widget'), standard_kivy_group)
            self.treeview.add_node(ListBoxEntry(text='RelativeLayout'), standard_kivy_group)
            self.treeview.add_node(ListBoxEntry(text='BoxLayout'), standard_kivy_group)