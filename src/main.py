import os
from pathlib import Path
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory 
from kivy.uix.boxlayout import BoxLayout

SRC_DIRECTORY = Path(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(SRC_DIRECTORY.parent, 'data') 
ICON_PATH = os.path.join(DATA_FOLDER, 'kivy-icon-48.png')

from kivy.core.window import Window


class RootWidget(BoxLayout):
    pass

class KivyDesignerApp(App):
    def build(self):
        self.title = 'Kivy Designer'
        root_widget = Builder.load_file(os.path.join(SRC_DIRECTORY, 'KivyDesigner.kv'))
        return root_widget

    def on_stop(self):
        '''Clean up application resources, such as Watchdog observer.
        '''
        pass

Factory.register('RootWidget', module='main')
Factory.register('KivyVisualizer', module='kivyvisualizer')
Factory.register('Toolbar', module='toolbar')
Factory.register('FileToolbarGroup', module='toolbar')

# Hot reloading kvlang for the root object is no issue at all
# Reloading updated python code is a lot tricker. My attempts
# to use importlib failed to update widget definitions. 
# more research required.
# I believe I need to reload the modules in the same original 
# order, which will require caching a dependency graph
from multiprocessing import Process, Queue
from visualizationsubprocess import VisualizationSubprocess, HotReloadInstruction

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
class ExampleRoot(Button):
    pass

class ExampleChild(App):
    def build(self):
        return ExampleRoot()

class UpdatedApp(App):
    def __init__(self, *kwargs):
        self.q = Queue()
        super().__init__(*kwargs)

    def build(self):
        box = BoxLayout()
        b = Button(text='Example')
        t = TextInput()
        b.bind(on_press=self.launchChild)
        t.bind(text=self.textChanged)
        box.add_widget(b)
        box.add_widget(t)
        return box

    def launchChild(self, button):
        p = Process(target=VisualizationSubprocess,args=(ExampleChild, self.q))
        p.start() 

    def textChanged(self, widget, text):
        # Just setup to trigger a reload with each keypress for now
        self.q.put(HotReloadInstruction("visualizationsubprocess"))

if __name__ == '__main__':
    #KivyDesignerApp().run()
    UpdatedApp().run()