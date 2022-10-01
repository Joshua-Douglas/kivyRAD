from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from plyer import filechooser

class Toolbar(BoxLayout):
    pass

class FileToolbarGroup(Button):
    '''FileToolbarGroup class. Custom Actionbar group for managing 
    file operations from the main application toolbar. 

    :Events:
        `on_open_file`
            Fired when a file is opened by the toolbar, either by creating
            a new file or selecting an existing file.
    '''

    __events__ = ['on_open_file']

    
    def __init__(self, **kwargs):
        super().__init__(text='File', background_color=(1,1,1,0), **kwargs)
        # Disable auto_width to allow the children buttons to 
        # be wider than the action group root button
        self._dropdown = DropDown(auto_width=False)
        self._dropdown.bind(on_select=self._dropdown_select)
        self._add_button('Open File', self._open_file)
        self._add_button('Open Folder', self._open_folder)
        self._add_button('New File', self._new_file)
    
    def _add_button(self, caption, btn_handler):
        btn = Button(text=caption, size_hint_y=None, height=24)
        # Bind the button event to dropdown.select() to properly dismiss
        # the dropdown menu. Pass the specific handler through the dropdown
        # selection. on_dropdown_select will invoke the handler. 
        btn.bind(on_release=lambda btn: self._dropdown.select(btn_handler))
        self._dropdown.add_widget(btn)

    def _dropdown_select(self, instance, selection_handler):
        if(not callable(selection_handler)):
            raise ValueError('FileToolbar dropdown selections should pass their OnPress event handler.')
        selection_handler()

    def on_press(self, *args):
        super().on_press(*args)
        self._dropdown.open(self)

    def _open_file(self):
        # User filechooser to select file
        # pass filename to dispatch function
        # Note: This will block the main thread, but that is
        # fine. We don't need to do anything until file is selected
        file_path = filechooser.open_file(title='Open kv file to visualize', 
          filters = [['kv file (*kv)', '*kv'], ['all', '*']])
        if file_path:
            # Default to first selection in the event of a multiselect
            with open(file_path[0], 'r', encoding='utf8') as reader:
                file_contents = reader.read()
                self.dispatch("on_open_file", file_path[0], file_contents)

    def _new_file(self):
        # use filechooser to set a new file name
        # pass filename to dispatch
        self.dispatch("on_open_file", "filename")

    def _open_folder(self):
        pass

    def on_open_file(self, opened_filename, opened_filetxt):
        pass