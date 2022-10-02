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

from kivy.uix.button import Button
from kivy.uix.textinput import TextInput 
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock 
import multiprocessing
from multiprocessing import Queue

class ChildAppStatic(App):
    def __init__(self, instruction_queue, *kwargs):
        self.instruction_queue = instruction_queue
        Clock.schedule_interval(self.process_external_instructions, 0.1)
        super().__init__(*kwargs)

    def build(self):
        self.b = Button(text='Child')
        return self.b

    def process_external_instructions(self, arg):
        if not self.instruction_queue.empty():
            latest_instruction = self.instruction_queue.get()
            self.b.text = latest_instruction

class ChildAppDynamic(App):
    def build(self):
        self.b = Button(text='child')
        return self.b 

def runStaic(instruction_queue):
    ChildAppStatic(instruction_queue).run()

'''
We could achieve the same thing by extending the ChildApp's type 
definition to include an instruction pipeline class variable and 
an instruction processing method and a scheduling method. 

This might not be necessary though, since we could probaly just
schedule and process the instructions outside of the app object. 
We'll just need access to rebuild the app using either a kvstring 
or updated python defintion. 

Let's get the simpel text variant working first before trying to swap
the window's widget.
def process_external_instructions(self, queue):
    if not queue.empty():
        latest_instruction = queue.get()
        self.b.text = latest_instruction

def runDynamic(instruction_queue):
    # Extend class type to add our instruction pipeline
    ChildAppDynamic.instruction_queue = instruction_queue
    ChildAppDynmaic.instruction_proc = 
'''

class ExampleApp(App):

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
        p = multiprocessing.Process(target=run,args=(self.q,))
        p.start() 

    def textChanged(self, widget, text):
        self.q.put(text)

if __name__ == '__main__':
    #KivyDesignerApp().run()
    ExampleApp().run()