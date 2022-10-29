from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.app import App

from kivydesigner.visualizationsubprocess import HotReloadInstruction

class KivyVisualizer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload_func_ref = App.get_running_app().hot_reload
        self.editor = CodeInput(do_wrap=False)
        self.editor.bind(text=self.handle_kv_change)
        self.add_widget(self.editor)

    def handle_kv_change(self, instance, value):
        self.reload_func_ref(HotReloadInstruction(value))

    def open_file(self, instance, new_filepath, new_filetxt):
        self.editor.text = new_filetxt