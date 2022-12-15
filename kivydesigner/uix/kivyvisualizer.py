from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.app import App

class KivyVisualizer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload_func_ref = App.get_running_app().hot_reload
        self.editor = CodeInput(do_wrap=False)
        self.editor.bind(text=self.handle_kv_change)
        self.add_widget(self.editor)

    def handle_kv_change(self, instance, value):
        self.reload_func_ref(value)

    def open_file(self, new_filepath):
        try:
            with open(new_filepath, 'r', encoding='utf8') as reader:
                self.editor.text = reader.read()
        except Exception as err:
            self.editor.text = f'Could not open {new_filepath} \n {str(err)}'
