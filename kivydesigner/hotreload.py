from dataclasses import dataclass
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import App
from kivy.base import EventLoop, stopTouchApp
from kivy.config import Config
from kivy.uix.label import Label

from multiprocessing import Queue
from queue import Empty
from functools import partial

@dataclass 
class KvStrInstruction:
    kv_str: str 
@dataclass 
class StopInstruction:
    pass

class HotReloadInstructionQueue:
    
    def __init__(self):
        self.queue = Queue()

    def reload_kvstring(self, kv_build_string: str):
        self.queue.put(KvStrInstruction(kv_build_string))

    def stop_reload(self):
        self.queue.put(StopInstruction())

    def empty(self):
        return self.queue.empty()

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

def _visualization_update(reload_queue, dt):
    if not reload_queue.empty():
        EventLoop.close()
    if EventLoop.status == 'started':
        # Restarting the application doesn't automatically refresh the window
        # since we are using a preexisting window instance. Force the refresh.
        win = EventLoop.window
        if win and win.canvas:
            win.canvas.ask_update()

def _tearDown():
    stopTouchApp()

def _setUp():
    # Currently the kivy input must be removed before continually 
    # reinstantiating the application. The windows providers, and 
    # possibly other provides for other platforms, currently 
    # throw a 'ArugmentError' during stopTouchApp because the input
    # providers are created without a window handle. If we can identify
    # why the providers are incorrectly recreated then we can support 
    # input in the visualized window. 
    for items in Config.items('input'):
        Config.remove_option('input', items[0])

def _visualize(app):
    '''kivy is designed to run a single application during an interpreter
    session. To run multiple application instances we need to do some
    special setup and teardown to ensure kivy's global variables are 
    properly initialized and finalized. 
    
    Setup kivy, run the app, and teardown. See setUp() and tearDown()
    for more information.
    '''
    _setUp()
    try:
        app.run()
    finally:
        _tearDown()

def run_visualization_app(hot_reload_queue: HotReloadInstructionQueue):
    '''
    Run a hot reload app, controlled by the hot_reload_queue. 
    The hot reload app is designed to run as the only kivy app within the 
    interpreter session. This method will block the thread, so it 
    must be run in a separate thread or process.

    See HotReloadInstructionQueue for full instruction set. 
    '''
    Clock.schedule_interval(partial(_visualization_update, hot_reload_queue), 0)   
    while hot_reload_queue.empty():
        continue 

    next_instruction = None
    while not isinstance(next_instruction, StopInstruction):
        next_instruction = hot_reload_queue.next_instruction()
        if isinstance(next_instruction, KvStrInstruction):
            _visualize(KvBuilderApp(kv_str=next_instruction.kv_str))
        elif next_instruction and not isinstance(next_instruction, StopInstruction):
            raise ValueError("Hot Reload type not recognized")

        # If no instruction is available, but we've exited _visualize, then the 
        # user manually stopped the visualized application. 
        next_instruction = next_instruction or StopInstruction()