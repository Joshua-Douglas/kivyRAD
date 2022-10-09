
from kivy.uix.button import Button
from kivy.graphics.svg import Svg
from kivy.graphics import Callback, Translate, Scale, Ellipse
from kivy.properties import StringProperty, ReferenceListProperty, NumericProperty

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
    svg_height = NumericProperty(1)
    svg_width = NumericProperty(1)

    def get_svg_size(self, filename):
        s = Svg(filename)
        return s.width, s.height

    def __init__(self, **kwargs):
        super(IconButton, self).__init__(**kwargs)
