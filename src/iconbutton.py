
from kivy.uix.button import Button
from kivy.graphics.svg import Svg
from kivy.properties import StringProperty, ReferenceListProperty, NumericProperty
from kivy.clock import Clock
from kivy.graphics import *

# I can load the svg into a fbo and then apply the fbo properties like 
# the texture to my current canvas. Fbo is an 'offscreen' canvas
class IconButton(Button):
    '''
    A standard kivy button that can design high resolution, rescalable
    SVG icons. 
    '''
    source = StringProperty('')

    width_padding = NumericProperty(0)
    height_padding = NumericProperty(0)
    padding = ReferenceListProperty([width_padding, height_padding])
    '''
    Padding between the button borders and the drawn svg image, in 
    pixels. 
    '''
    def __init__(self, **kwargs):
        super(IconButton, self).__init__(**kwargs)
        with self.canvas.after:
            self.translation = Translate()
            self.scale = Scale()
            self.svg = Svg()
            self.iscale = Scale()
            self.itranslation = Translate()
        Clock.schedule_once(self.draw_svg)

    def _calc_scalefactor(self, svg_instruct):
        svg_width, svg_height = svg_instruct.width, svg_instruct.height
        x_sf = (self.width - 2 * self.width_padding) / svg_width 
        y_sf = (self.height - 2 * self.height_padding) / svg_height
        return x_sf, y_sf
            
    def draw_svg(self, *args):
        self.svg.source = self.source 
        x_sf, y_sf = self._calc_scalefactor(self.svg) 
        self.scale.x = x_sf 
        self.scale.y = y_sf 
        self.iscale.x = 1/x_sf 
        self.iscale.y = 1/y_sf
        self.translation.x = self.x 
        self.translation.y = self.y 
        self.itranslation.x = -self.x 
        self.itranslation.y = -self.y 

    def on_source(self, *args):
        self.draw_svg()

    def on_pos(self, *args):
        self.draw_svg()

    def on_size(self, *args):
        self.draw_svg()

if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.lang import Builder
    ex_kv = r'''
BoxLayout:
    Button:
        text: 'first'
    IconButton:
        source: "C:\\Users\\joshu\\source\\repos\\kivydesigner\\src\\pumk.svg"
    Button:
        text: 'second'
    '''
    root = Builder.load_string(ex_kv)
    runTouchApp(root)