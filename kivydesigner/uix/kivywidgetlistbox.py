from pathlib import Path
import copy
import site

from kivy.clock import Clock
from kivy.properties import StringProperty
from kivydesigner.uix.grouplistbox import GroupListBox
from kivydesigner.inheritancetrees import InheritanceTreesBuilder

class KivyWidgetListBox(GroupListBox):

    project_path = StringProperty(None, allow_none=True)
    '''Search path used to populate the listbox with user defined widgets and apps.
    If None, the listbox will only contain the standard kivy widgets and apps.'''
    kivy_inheritance_tree = InheritanceTreesBuilder.kivy_widget_tree().tree
    '''Static reference to inheritance tree populated with kivy standard library widgets and apps.'''
    standard_library_apps = kivy_inheritance_tree.get_subclasses('App')
    '''Static set of all kivy standard library apps.'''
    standard_library_widgets = kivy_inheritance_tree.get_subclasses('Widget')
    '''Static set of all kivy standard library widgets.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inheritance_tree = copy.copy(KivyWidgetListBox.kivy_inheritance_tree)
        
    def on_project_path(self, instance, value):
        '''
        Update the list of user defined widgets when the project path changes.
        '''
        self.update_user_defined_widgets()

    def update_user_defined_widgets(self):
        '''
        Flush all previous user defined widgets and apps from inheritance tree
        and treeview, and repopulate the treeview with the user defined widgets
        in the project path.

        The project path must be a valid directory. 
        '''
        self.clear()
        if not (self.project_path and Path(self.project_path).is_dir()):
            self.add_group('STANDARD KIVY APPS', self.standard_library_apps)
            self.add_group('STANDARD KIVY WIDGETS', self.standard_library_widgets)
            return

        builder = InheritanceTreesBuilder()
        builder.tree = self.inheritance_tree

        # Search project path for user defined widgets and apps.
        # Exclude external packages from search.
        dirs_to_exclude = [Path(path) for path in site.getsitepackages()]
        builder.build_from_directory(self.project_path,
            lambda filepath: not any(filepath.is_relative_to(parent) for parent in dirs_to_exclude)) 

        user_defined_widgets = self.inheritance_tree.get_subclasses('Widget')
        user_defined_widgets -= self.standard_library_widgets
        user_defined_apps = self.inheritance_tree.get_subclasses('App')
        user_defined_apps -= self.standard_library_apps

        self.add_group('USER DEFINED APPS', user_defined_apps)
        self.add_group('USER DEFINED WIDGETS', user_defined_widgets)
        self.add_group('STANDARD KIVY WIDGETS', self.standard_library_widgets)
        self.add_group('STANDARD KIVY APPS', self.standard_library_apps)

    def clear(self):
        super().clear()
        self.inheritance_tree = copy.copy(KivyWidgetListBox.kivy_inheritance_tree)

