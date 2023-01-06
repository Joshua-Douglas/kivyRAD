from pathlib import Path
import copy

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivydesigner.uix.grouplistbox import GroupListBox
from kivydesigner.inheritancetrees import InheritanceTreesBuilder

class KivyWidgetListBox(GroupListBox):

    project_path = StringProperty(None, allow_none=True)
    kivy_inheritance_tree = InheritanceTreesBuilder.kivy_widget_tree().tree
    standard_library_apps = kivy_inheritance_tree.get_subclasses('App')
    standard_library_widgets = kivy_inheritance_tree.get_subclasses('Widget')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inheritance_tree = copy.copy(KivyWidgetListBox.kivy_inheritance_tree)
        Clock.schedule_once(self.update_user_defined_widgets, 0)
        
    def on_project_path(self, instance, value):
        '''
        Update the list of user defined widgets when the project path changes.
        '''
        self.update_user_defined_widgets()

    def update_user_defined_widgets(self, dt=0):
        '''
        Flush all previous user defined widgets and apps from inheritance tree
        and treeview, and repopulate the treeview with the user defined widgets
        in the project path.

        The project path must be a valid directory. 
        '''
        self.clear()
        '''
        To-Do:
        1) Why is this method called multiple times at startup? We should avoid multiple
        calls to the expensive InheritanceTreesBuilder.build_from_directory method.
        2) build_from_directory is failing for some reason. It is not finding the
        user defined widgets in the project path.
        3) Clear() is not removing the user defined groups from the treeview.
        '''
        if not (self.project_path and Path(self.project_path).is_dir()):
            return

        builder = InheritanceTreesBuilder()
        builder.tree = self.inheritance_tree
        builder.build_from_directory(self.project_path)

        user_defined_widgets = self.inheritance_tree.get_subclasses('Widget')
        user_defined_widgets -= self.standard_library_widgets
        user_defined_apps = self.inheritance_tree.get_subclasses('App')
        user_defined_apps -= self.standard_library_apps

        self.add_group('USER DEFINED APPS', user_defined_apps)
        self.add_group('USER DEFINED WIDGETS', user_defined_widgets)
        self.add_group('STANDARD KIVY APPS', self.standard_library_apps)
        self.add_group('STANDARD KIVY WIDGETS', self.standard_library_widgets)

    def clear(self):
        super().clear()
        self.inheritance_tree = copy.copy(KivyWidgetListBox.kivy_inheritance_tree)

