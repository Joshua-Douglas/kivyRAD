from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

class Toolbar(BoxLayout):
    pass

class FileToolbarGroup(Button):

    def __init__(self, **kwargs):
        super().__init__(text='File', background_color=(1,1,1,0), **kwargs)
        # Disable auto_width to allow the children buttons to 
        # be wider than the action group root button
        self._dropdown = DropDown(auto_width=False)
        self._dropdown.bind(on_select=self.on_dropdown_select)
        self._add_button('Open File', self.on_open_file)
        self._add_button('Open Folder', self.on_open_folder)
    
    def _add_button(self, caption, btn_handler):
        btn = Button(text=caption, size_hint_y=None, height=24)
        # Bind the button event to dropdown.select() to properly dismiss
        # the dropdown menu. Pass the specific handler through the dropdown
        # selection. on_dropdown_select will invoke the handler. 
        btn.bind(on_release=lambda btn: self._dropdown.select(btn_handler))
        self._dropdown.add_widget(btn)

    def on_dropdown_select(self, instance, selection_handler):
        if(not callable(selection_handler)):
            raise ValueError('FileToolbar dropdown selections should pass their OnPress event handler.')
        selection_handler()

    def on_press(self, *args):
        super().on_press(*args)
        self._dropdown.open(self)

    def on_open_file(self, *args):
        pass

    def on_open_folder(self, *args):
        pass