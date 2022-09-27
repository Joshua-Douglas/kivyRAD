import os
from pathlib import Path
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory 

SRC_DIRECTORY = Path(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(SRC_DIRECTORY.parent, 'data') 
ICON_PATH = os.path.join(DATA_FOLDER, 'kivy-icon-48.png')

class KivyDesignerApp(App):
    def build(self):
        self.title = 'Kivy Designer'
        root_widget = Builder.load_file(os.path.join(SRC_DIRECTORY, 'KivyDesigner.kv'))
        return root_widget

    def on_stop(self):
        '''Clean up application resources, such as Watchdog observer.
        '''
        pass

Factory.register('KivyVisualizer', module='kivyvisualizer')
Factory.register('Toolbar', module='toolbar')
Factory.register('FileToolbarGroup', module='toolbar')

if __name__ == '__main__':
    KivyDesignerApp().run()
