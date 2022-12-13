from pathlib import Path
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty

kv_filepath = Path(__file__).with_suffix('.kv')
Builder.load_file(str(kv_filepath), rulesonly=True)

class ModalMsg(ModalView):
    title = StringProperty('Kivy Designer')
    message = StringProperty('')
    icon_name = StringProperty('info')
    yes_btn_text = StringProperty('Yes')
    yes_btn_width = NumericProperty(60)
    cancel_btn_text = StringProperty('Cancel')
    cancel_btn_width = NumericProperty(60)

    __events__ = ('on_close',)

    def on_close(self, response):
        pass

    def on_btn_release(self, response):
        self.dismiss()
        self.dispatch("on_close", response)

    def open(self, on_close_handler=None, *args, **kwargs):
        if on_close_handler:
            self.bind(on_close=on_close_handler)
        super().open(*args, **kwargs)

if __name__ == '__main__':
    from kivy.app import runTouchApp
    dialog = ModalMsg(message='This is an example message. Would the user like to proceed?')
    dialog.open(lambda obj, resp: print(f'User selected {resp}'))
    runTouchApp()