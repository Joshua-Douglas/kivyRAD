from dataclasses import dataclass
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.app import App
from kivy.base import EventLoop, stopTouchApp
from kivy.config import Config
        

from kivy.uix.label import Label
from kivy.uix.widget import Widget
from multiprocessing import Queue
from queue import Empty

@dataclass 
class WidgetInstruction:
    widget_type: type[Widget]
@dataclass 
class KvFileInstruction:
    kv_filepath: str 
@dataclass 
class KvStrInstruction:
    kv_str: str 
@dataclass 
class StopInstruction:
    pass

class HotReloadInstructionQueue:
    
    def __init__(self):
        self.queue = Queue()

    def reload_kvfile(self, kv_filepath: str):
        self.queue.put(KvStrInstruction(kv_filepath))
    
    def reload_kvstring(self, kv_build_string: str):
        self.queue.put(KvStrInstruction(kv_build_string))

    def reload_widget(self, widget_cls: type[Widget]):
        self.queue.put(WidgetInstruction(widget_cls))

    def stop_reload(self):
        self.queue.put(StopInstruction())

    def next_instruction(self):
        try:
            return self.queue.get(block=False)
        except Empty:
            return None

class KvBuilderApp(App):

    def __init__(self, kv_str, **kwargs):
        super(KvBuilderApp, self).__init__(**kwargs)
        self.kv_str = kv_str 

    def build(self):
        try:
            root = Builder.load_string(self.kv_str)
        except Exception as builderr:
            root = Label(text=str(builderr))
        return root

class VisualizationSubprocess:
    '''
    This class is designed to perform a hot reload kivy 
    applications that are executing in a subprocess. 

    The parent process can signal a reload by pushing a
    hot reload instruction onto the processing queue. The
    processing queue should be populated with `HotReloadInstruction`s. 
    '''

    def __init__(self, hot_reload_queue_ref: HotReloadInstructionQueue): 
        self.reload_queue = hot_reload_queue_ref
        self.current_instruction = None

        # on_window_flip will listen for hot reload instructions
        # and stop the application any time an instruction is received
        Window.bind(on_flip=self.on_window_flip)

        self.visualize(KvBuilderApp(kv_str='Widget'))       
        while True:
            if not self.current_instruction:
                continue

            if isinstance(self.current_instruction, StopInstruction):
                break 
            elif isinstance(self.current_instruction, KvStrInstruction):
                self.visualize(KvBuilderApp(kv_str=self.current_instruction.kv_str))
            else:
                raise ValueError("Hot Reload type not recognized")

        Window.unbind(on_flip=self.on_window_flip)

    def on_window_flip(self, window):
        self.current_instruction = self.reload_queue.next_instruction() 
        if self.current_instruction:
            EventLoop.close()

    def _force_refresh(self, *largs):
        '''Force a refresh of the window canvas.'''
        win = EventLoop.window
        if win and win.canvas:
            win.canvas.ask_update()

    def visualize(self, app):
        '''kivy is designed to run a single application during an interpreter
        session. To run multiple application instances we need to do some
        special setup and teardown to ensure kivy's global variables are 
        properly initialized and finalized. 
        
        Setup kivy, run the app, and teardown. See setUp() and tearDown()
        for more information.
        '''
        self.setUp()

        try:
            # Restarting the application doesn't automatically refresh the window
            # since we are using a preexisting window instance. Force the refresh.
            Clock.schedule_interval(self._force_refresh, 1)
            app.run()
        finally:
            Clock.unschedule(self._force_refresh)

        self.tearDown()

    def tearDown(self):
        stopTouchApp()

    def setUp(self):
        # Currently the kivy input must be removed before continually 
        # reinstantiating the application. The windows providers, and 
        # possibly other provides for other platforms, currently 
        # throw a 'ArugmentError' during stopTouchApp because the input
        # providers are created without a window handle. If we can identify
        # why the providers are incorrectly recreated then we can support 
        # input in the visualized window. 
        for items in Config.items('input'):
            Config.remove_option('input', items[0])