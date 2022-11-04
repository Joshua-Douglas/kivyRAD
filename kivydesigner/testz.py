from kivy.app import App
from kivy.uix.button import Button 
from kivy.uix.boxlayout import BoxLayout
from threading import Thread
import time
from kivy.base import stopTouchApp
    
class App1(App):

    def build(self):
        b = BoxLayout()
        for i in range(7):
            btn = Button(text='first') 
            b.add_widget(btn)
        return b

class App2(App):

    def build(self):
        b = BoxLayout()
        for i in range(3):
            btn = Button(text='second') 
            b.add_widget(btn)
        return b

a = None
done = False
cntr = 0

def _listen_for_updates():
        '''
        Wait until a hot reload request is available, then 
        apply the hot reload. This method will block the 
        thread it is executing in.
        '''
        global a
        while not done: 
            time.sleep(.05)
            if a:
                stopTouchApp()
                #reset()
                a = None

listen_task = Thread(target=_listen_for_updates)
listen_task.start()

def runandrestart():
    global a
    global cntr 
    if cntr % 2 == 0:
        a = App1()
    else:
        a = App2()
    cntr += 1
    a.run()

for i in range(100):
    runandrestart()

done = True
listen_task.join()