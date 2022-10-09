import os
from pathlib import Path
from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory 
from kivy.uix.boxlayout import BoxLayout

import multiprocessing
from visualizationsubprocess import VisualizationSubprocess

SRC_DIRECTORY = Path(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(SRC_DIRECTORY.parent, 'data') 
ICON_PATH = os.path.join(DATA_FOLDER, 'kivy-icon-48.png')

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
        self.visualization_instructions = multiprocessing.Queue()
        self.visualization_subprocess = None
        root_widget = Builder.load_file(os.path.join(SRC_DIRECTORY, 'KivyDesigner.kv'))
        return root_widget

    def on_stop(self):
        '''
        Gracefully terminate the visualization subprocess when the kivy 
        designer is stopped.
        '''
        if self._is_visualizing():
            self.visualization_subprocess.terminate()

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
        Run the VisualizationSubprocess on a new child
        process. VisualizationSubprocess will create 
        and visualize cls_app_to_visualize. Hot reloads
        can be performed by putting reload instructions
        onto the visualization_instructions queue. 
        '''
        new_process = multiprocessing.Process(
            target=VisualizationSubprocess,
            args=(self.visualization_instructions,)
        )
        new_process.start()
        self.visualization_subprocess = new_process

    def hot_reload(self, reload_instruction):
        if not self._is_visualizing():
            self._start_visualizing()
        self.visualization_instructions.put(reload_instruction) 

Factory.register('RootWidget', module='main')
Factory.register('KivyVisualizer', module='kivyvisualizer')
Factory.register('Toolbar', module='toolbar')
Factory.register('FileToolbarGroup', module='toolbar')

if __name__ == '__main__':
    KivyDesignerApp().run()