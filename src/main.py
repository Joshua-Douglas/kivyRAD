import os
from pathlib import Path
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

DATA_FOLDER = os.path.join(Path(os.path.dirname(__file__)).parent, 'data') 
ICON_PATH = os.path.join(DATA_FOLDER, 'kivy-icon-48.png')

class KivyDesignerRoot(BoxLayout):
    pass

class KivyDesignerApp(App):
    def build(self):
        return KivyDesignerRoot()

if __name__ == '__main__':
    KivyDesignerApp().run()
