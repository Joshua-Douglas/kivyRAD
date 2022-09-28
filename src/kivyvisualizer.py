from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder

class KivyEditor(TextInput):
    # Note: I can use extras\highlight.py to syntax highlight the editor text!!
    # Actualy codeinput.py provides this 'out of the box' functionality 
    def __init__(self):
        super().__init__()

class KivyVisualizer(BoxLayout):
    # kivy's parser.py has a 'proxyapp'. Can I use this approach instead of choosing to insert the root widget?
    # There is also a 'Sandbox' widget that does the type of error catching we need...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.editor = KivyEditor()
        self.visualizer = BoxLayout()
        self.editor.bind(text=self.handle_kv_change)
        self.add_widget(self.editor)
        self.add_widget(self.visualizer)

    def handle_kv_change(self, instance, value):
        self.visualizer.clear_widgets()
        
        if not value: 
            return 

        try:
            new_app = Builder.load_string(value)
        except Exception as e: 
            new_app = Label(text=str(e))

        self.visualizer.add_widget(new_app)