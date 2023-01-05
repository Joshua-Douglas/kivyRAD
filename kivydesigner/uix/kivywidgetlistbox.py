from kivy.clock import Clock

from kivydesigner.uix.grouplistbox import GroupListBox
from kivydesigner.inheritancetrees import InheritanceTreesBuilder

class KivyWidgetListBox(GroupListBox):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.populate_treeview, 0)

    def populate_treeview(self, dt):
        kivy_builder = InheritanceTreesBuilder.kivy_widget_tree()
        self.inheritance_tree = kivy_builder.tree
        self.standard_library_widgets = self.inheritance_tree.get_subclasses('Widget')
        self.standard_library_apps = self.inheritance_tree.get_subclasses('App')

        self.add_group('STANDARD KIVY APPS', self.standard_library_apps)
        self.add_group('STANDARD KIVY WIDGETS', self.standard_library_widgets)

