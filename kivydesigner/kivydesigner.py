import os
from pathlib import Path
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

import multiprocessing
from kivydesigner.hotreload import run_visualization_app, HotReloadInstructionQueue

class RootWidget(BoxLayout):
    pass

class KivyDesignerApp(App):
    '''
    The main application. 
    Provides a range of tools to allow users to build 
    and visualize kivy applications in real time. To 
    maximize accuracy, the kivy application is visualized
    in a child process. This process currently runs with
    the same version of python and kivy as the KivyDesigner, 
    and does not provide any options for configuring the 
    kivy environment. 

    Updates to the visualized applications are triggered 
    by sending a HotReloadInstruction to the child process,
    through a multiprocessing Queue.  
    '''
    def build(self):
        self.title = 'Kivy Designer'
        self.visualization_instructions = HotReloadInstructionQueue()
        self.visualization_subprocess = None
        return super().build()

    def on_stop(self):
        '''
        Gracefully terminate the visualization subprocess when the kivy 
        designer is stopped.
        '''
        if self._is_visualizing():
            self.visualization_instructions.stop_reload()
            self.visualization_subprocess.join()

    def _is_visualizing(self):
        '''
        Return true if a kivy visualizer subprocess is running. 
        Return false otherwise.
        '''
        result = self.visualization_subprocess is not None
        if result:
            try:
                result = self.visualization_subprocess.is_alive()
            except ValueError as e:
                # is_alive will throw a ValueError if the process is 
                # already closed
                result = False

        # We know the subprocess is no longer valid. Clear our ref
        if not result and self.visualization_subprocess:
            self.visualization_subprocess = None 
        return result

    def _start_visualizing(self):
        '''
        Run the VisualizationSubprocess on a new child process. 
        Hot reloads can be performed by putting reload instructions
        onto the visualization_instructions queue. 
        '''
        # We are taking special care to avoid creating VisualizationSubprocess within
        # this interpreter session to avoid initializing the VisualizationSubprocess 
        # app using the KivyDesignerApp config. Kivy's initialization relies on global 
        # singletons, so mixing the environments will cause the visualization to fail.
        new_process = multiprocessing.Process(
            target=run_visualization_app,
            args=(self.visualization_instructions,)
        )
        new_process.start()
        self.visualization_subprocess = new_process

    def hot_reload(self, new_kv_str):
        if not self._is_visualizing():
            self._start_visualizing()
        self.visualization_instructions.reload_kvstring(new_kv_str) 