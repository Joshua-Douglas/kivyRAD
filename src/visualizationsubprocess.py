import importlib
from dataclasses import dataclass
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder

@dataclass
class HotReloadInstruction:
    py_module_to_reload: str 

class VisualizationSubprocess:
    '''
    This class is designed to perform a hot reload kivy 
    applications that are executing in a subprocess. 

    The parent process can signal a reload by pushing an 
    updated kvlang string onto the processing queue. The
    processing queue should be populated with `HotReloadInstruction`s. 
    '''
    def __init__(self, cls_reload_app, hot_reload_queue_ref):
        # Note: Should probably add an error pipe so I can 
        # send exceptions back 
        if not isinstance(cls_reload_app, type):
            raise ValueError(f'Type expected for cls_reload_app, but {type(cls_reload_app)} found')
        
        # Save the files registerd with the builder before constructing the 
        # child app. This will allow us to unload each of the new application's
        # files while hot reloading
        self.builder_file_cache = Builder.files[:]
        self.reload_app = cls_reload_app()

        self.reload_queue = hot_reload_queue_ref
        Clock.schedule_interval(self.hot_reload, 0.1)

        self.reload_app.run()

    def _unload_builder_files(self):
        '''
        Unload all of the files loaded into the kivy Builder, 
        except the default files stored in self.builder_file_cache.

        Unloading the kivy files also unregisters the class from the
        kivy Factory. Unloading works for registered strings too, since
        strings are assigned a pseudo filename.
        '''
        for file in Builder.files[:]:
            if file not in self.builder_file_cache:
                Builder.unload_file(file)
        
    def hot_reload(self, *args):
        '''
        Check the processing queue for reload instructions. 
        Perform the first instruction in the queue, if available.

        Note: In the future we could read to the last item and just
        perform the last since each task overwrites the previous. 
        '''
        # Note: Checking an mulitprocessing queue will block the
        # current thread. A return value of True from empty() does
        # not guarentee that the queue will not block, since other users
        # of the queue could empty it before our access. This class should
        # be the only actor poping from the queue. Disable blocking
        # and purposefully do not handle 'Empty' exceptions to enforce this.
        if self.reload_queue.empty():
            return 

        # Kivy does not provide any application reload functionality
        # Clear the existing widgets and rebuild without closing
        # the application window or exiting the event loop
        for child in self.reload_app._app_window.children[:]:
            self.reload_app._app_window.remove_widget(child)
        self._unload_builder_files()
        self.reload_app.built = False
        self.reload_app.root = None

        reload_instruction = self.reload_queue.get()
        if reload_instruction.py_module_to_reload:
            # Remove items from Factory? Or will reload handle?
            module_to_reload = importlib.import_module(reload_instruction.py_module_to_reload)
            importlib.reload(module_to_reload)

        self.reload_app._run_prepare()

