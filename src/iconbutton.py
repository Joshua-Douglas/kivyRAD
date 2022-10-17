
from kivy.uix.button import Button
from kivy.graphics.svg import Svg
from kivy.properties import StringProperty, ReferenceListProperty, NumericProperty
from kivy.clock import Clock
from kivy.graphics import Translate, Scale

class IconButton(Button):
    '''
    A standard kivy button that can display high resolution, rescalable
    SVG icons. 
    '''
    source = StringProperty('')

    width_padding = NumericProperty(0)
    height_padding = NumericProperty(0)
    svg_padding = ReferenceListProperty(width_padding, height_padding)
    '''
    Padding between the button borders and the drawn svg image, in 
    pixels. 
    '''
    def __init__(self, **kwargs):
        super(IconButton, self).__init__(**kwargs)
        # Add the drawing and translation instructions to the 
        # canvas. Store references to the instructions to 
        # allow updates as necessary. Translation and scaling
        # is necessary to transform the SVG from global coords
        # to button coords.
        with self.canvas.after:
            self.translation = Translate()
            self.scale = Scale()
            self.svg = Svg()
            self.iscale = Scale()
            self.itranslation = Translate()
        Clock.schedule_once(self.draw_svg)
           
    def _update_svg_src(self):
        '''Update the svg source, and 
        reload the svg file.
        '''
        self.svg.source = self.source

    def _update_svg_size(self):
        '''Update scaling instruction.
        Scale the svg to fill the entire button
        area, minus the padding area. Also set the 
        inverse sacling to prevent impacting downstream
        instructions. 
        '''
        svg_width, svg_height = self.svg.width, self.svg.height
        x_sf = (self.width - 2 * self.width_padding) / svg_width 
        y_sf = (self.height - 2 * self.height_padding) / svg_height
        self.scale.xyz = x_sf, y_sf, 1
        # Avoid divide by zero error using short-circuiting logic
        # Note: inverse scaling if the user specifies an overly
        # large padding is fine. 
        self.iscale.x = x_sf and 1/x_sf
        self.iscale.y = y_sf and 1/y_sf

    def _update_svg_pos(self, *args):
        '''Update translation instruction. 
        Translate the svg instruction to the button's 
        origin plus padding. Also set the inverse translation
        to prevent impacting downstream instructions. 
        '''
        x_trans, y_tras = self.x + self.width_padding, self.y + self.height_padding
        self.translation.xy = x_trans, y_tras
        self.itranslation.xy = -x_trans, -y_tras

    def draw_svg(self, *args):
        '''Refresh each of the canvas instructions to 
        draw the svg image on the button.
        '''
        # Must update the svg src before the 
        # size update, since the scale factor
        # depends on the svg size
        self._update_svg_src()
        self._update_svg_size()
        self._update_svg_pos()

    def on_source(self, *args):
        self._update_svg_src()

    def on_pos(self, *args):
        self._update_svg_pos()

    def on_size(self, *args):
        self._update_svg_size()

if __name__ == '__main__':
    from kivy.app import runTouchApp
    from kivy.lang import Builder
    ex_kv = r'''
BoxLayout:
    Button:
        text: 'first'
    IconButton:
        source: ".\\data\\blue.svg"
        text: "hidden"
        svg_padding: 25, 50
    Button:
        text: 'second'
    '''
    root = Builder.load_string(ex_kv)
    runTouchApp(root)