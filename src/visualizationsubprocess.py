from threading import Thread
from dataclasses import dataclass
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.app import App
from functools import partial

from kivy.uix.label import Label
from kivy.uix.widget import Widget
from enum import Enum, auto

@dataclass
class HotReloadInstruction:
    '''
    Hot Reload Instruction set supported 
    by the VisualizationSubprocess. The visualized
    app can be directed by pushing one or more 
    reload instructions onto the subprocess 
    instruction queue. 
    '''
    kivy_build_str: str = ''

class ListenerInstructions(Enum):
    '''
    Internal class used by VisualizationSubprocess
    to control the listening task
    '''
    STOPLISTENING = auto()
    '''Stop listening for reload instructions and complete task execution'''

class HotReloadApp(App):
    '''
    Application used to host the visualized root widget. 

    Reloads are currently achieved by swapping the root widget.
    '''

    def __init__(self, *kwargs): 
        self.build_func = Label
        self.registered_build_files = set()
        return super(HotReloadApp, self).__init__(*kwargs)

    def build(self):
        '''
        Unregister previously loaded builder files and 
        build the root widget.
        '''
        for file in self.registered_build_files:
            Builder.unload_file(file)
        self.registered_build_files = set()

        files_before_build = set(Builder.files[:])
        new_root = self.build_func() 
        files_after_build = set(Builder.files[:])

        self.registered_build_files = files_after_build - files_before_build
        return new_root
  
    def update(self, build_func=None):
        '''
        Clear all widgets from the application window, unload all
        files previously registered with the kivy Builder, and 
        add a new root widget using the widget returned by 
        build_func. 
        '''
        if build_func:
            self.build_func = build_func 

        for widget in Window.children[:]:
            Window.remove_widget(widget)

        try:
            new_root = self.build()
            Window.add_widget(new_root)
        except Exception as builderr:
            Window.add_widget(Label(text=str(builderr)))

class VisualizationSubprocess:
    '''
    This class is designed to perform a hot reload kivy 
    applications that are executing in a subprocess. 

    The parent process can signal a reload by pushing a
    hot reload instruction onto the processing queue. The
    processing queue should be populated with `HotReloadInstruction`s. 
    '''
    def __init__(self, hot_reload_queue_ref):       
        self.reload_queue = hot_reload_queue_ref
        self.listen_task = Thread(target=self._listen_for_updates)
        self.reload_app = HotReloadApp()
        
        self.listen_task.start()
        try:
            self.reload_app.run()
        finally:
            # Application is no longer running. Instruct
            # the listening task to finish, and 
            # wait for thread execution to complete
            self.reload_queue.put(ListenerInstructions.STOPLISTENING)
            self.listen_task.join()
            self.listen_task = None

    def _listen_for_updates(self):
        '''
        Wait until a hot reload request is available, then 
        apply the hot reload. This method will block the 
        thread it is executing in.
        '''
        while True: 
            next_instruction = self.reload_queue.get()

            if next_instruction == ListenerInstructions.STOPLISTENING:
                return

            Clock.schedule_once(partial(self._hot_reload, next_instruction))

    def _hot_reload(self, instruction, delta_time):
        '''
        Determine the correct handler for the provided hot reload 
        instruction, and trigger the visualized app update. 

        Hot reload handlers must provide an updated root widget.
        '''
        # Only one instuction is currently available
        if instruction.kivy_build_str:
            handler = lambda: Builder.load_string(instruction.kivy_build_str)
        else:
            # An empty build string was specified. Pass an empty widget
            handler = Widget
        self.reload_app.update(build_func=handler)




