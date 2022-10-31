import kivy.base
from kivy.base import EventLoop

# This monkey-patch is heading the right direction. 

# I may need to monkey-patch a few more things because I'm 
# getting an error associated with one of the input providers, 
# but if this approach works then we will be able to safely call
# app.Stop() and app.run() to restart the application. Once 
# we actually need to terminate the application we will need 
# to manully call the un-monkey patched version of stopTouchApp.
def stopTouchApp():
    if EventLoop.status != 'started':
        return
    # XXX stop in reverse order that we started them!! (like push
    # pop), very important because e.g. wm_touch and WM_PEN both
    # store old window proc and the restore, if order is messed big
    # problem happens, crashing badly without error
    for provider in reversed(EventLoop.input_providers[:]):
        provider.stop()
        EventLoop.remove_input_provider(provider)

    # ensure any restart will not break anything later.
    EventLoop.input_events = []

kivy.base.stopTouchApp = stopTouchApp
from kivy.app import App


from kivy.uix.button import Button 
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

app = None

def do_swap(instance):
    global app
    app.stop()
    def do_run():
        if isinstance(app, App1):
            app = App1()
        else:
            app = App2()
        app.run()
    app.run()
    
class App1(App):

    def build(self):
        b = BoxLayout()
        for i in range(7):
            btn = Button(text='first') 
            btn.bind(on_press=do_swap)
            b.add_widget(btn)
        return b

class App2(App):

    def build(self):
        b = BoxLayout()
        for i in range(7):
            btn = Button(text='second') 
            btn.bind(on_press=do_swap)
            b.add_widget(btn)
        return b

app = App1()
app.run()
