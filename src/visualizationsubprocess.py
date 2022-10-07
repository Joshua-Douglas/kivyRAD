from threading import Thread
from dataclasses import dataclass
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.app import App
from functools import partial

from kivy.uix.label import Label

@dataclass
class HotReloadInstruction:
    kivy_build_str: str 

class HotReloadApp(App):

    def __init__(self, build_func, *kwargs): 
        self.build_func = build_func
        self.registered_build_files = set()
        return super(HotReloadApp, self).__init__(*kwargs)

    def build(self):
        files_before_build = set(Builder.files[:])
        new_root = self.build_func() 
        files_after_build = set(Builder.files[:])
        self.registered_build_files = files_after_build - files_before_build
        return new_root
  
    def update(self, build_func=None):
        if build_func:
            self.build_func = build_func 

        for file in self.registered_build_files:
            Builder.unload_file(file)

        for widget in Window.children[:]:
            Window.remove_widget(widget)

        try:
            new_root = self.build_func()
            Window.add_widget(new_root)
        except Exception as builderr:
            Window.add_widget(Label(text=str(builderr)))

class VisualizationSubprocess:
    '''
    This class is designed to perform a hot reload kivy 
    applications that are executing in a subprocess. 

    The parent process can signal a reload by pushing an 
    updated kvlang string onto the processing queue. The
    processing queue should be populated with `HotReloadInstruction`s. 
    '''
    def __init__(self, cls_app_to_visualize, hot_reload_queue_ref):       
        self.reload_queue = hot_reload_queue_ref
        self.listen_task = Thread(target=self.listen_for_updates)
        self.reload_app = HotReloadApp(build_func=cls_app_to_visualize().build)
        
        self.listen_task.start()
        self.reload_app.run()

    def __del__(self):
        self.listen_task.join()

    def listen_for_updates(self):
        '''
        Wait until a hot reload request is available, then 
        apply the hot reload. This method will block the 
        thread it is executing in.
        '''
        while True: 
            next_instruction = self.reload_queue.get()
            Clock.schedule_once(partial(self.hot_reload, next_instruction))

    def hot_reload(self, instruction, delta_time):
        def b():
            return Builder.load_string(instruction.kivy_build_str)
        self.reload_app.update(build_func=b)




