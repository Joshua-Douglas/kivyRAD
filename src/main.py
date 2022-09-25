import os
from pathlib import Path
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

SRC_DIRECTORY = Path(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(SRC_DIRECTORY.parent, 'data') 
ICON_PATH = os.path.join(DATA_FOLDER, 'kivy-icon-48.png')

class KivyDesignerApp(App):
    def build(self):
        self.title = 'Kivy Designer'
        root_widget = Builder.load_file(os.path.join(SRC_DIRECTORY, 'KivyDesigner.kv'))
        Clock.schedule_once(self.insert_visualizer, 1)
        return root_widget

    def on_stop(self):
        '''Clean up application resources, such as Watchdog observer.
        '''
        pass

    def insert_visualizer(self, *args):
        '''
        Insert a test widget within the visualizer's layout

        The production version will pass a path option that coincides with the 
        editor file. 
        '''
        visualizer = Builder.load_file(os.path.join(SRC_DIRECTORY, 'Visualizer.kv'))
        self.root.ids.visualizer_widget.add_widget(visualizer)

if __name__ == '__main__':
    KivyDesignerApp().run()
