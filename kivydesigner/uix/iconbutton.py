from kivy.uix.button import Button
from kivy.graphics.svg import Svg
from kivy.properties import StringProperty, ReferenceListProperty, NumericProperty
from kivy.clock import Clock
from kivy.graphics import Translate, Scale
from xml.etree.ElementTree import ElementTree, XML


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
        # Add the drawing and translation instructions to the 
        # canvas. Store references to the instructions to 
        # allow updates as necessary. Translation and scaling
        # is necessary to transform the SVG from global coords
        # to button coords.
        super(IconButton, self).__init__(**kwargs)
        with self.canvas.after:
            self.translation = Translate()
            self.scale = Scale()
            self.svg = Svg()
            self.iscale = Scale()
            self.itranslation = Translate()
        Clock.schedule_once(self.draw_svg)
           
    def _update_svg_src(self):
        '''Update the svg source, and reload the svg file.'''
        # SVG instruction must have a valid file. If file is invalid, 
        # then manually clear the SVG instruction tree by passing 
        # an empty ElementTree() 
        if self.source:
            self.svg.source = self.source
        else:
            self.clear_svg()

    def clear_svg(self):
        self.source = ''
        empty_root = XML("<svg width='1' height='1'></svg>")
        empty_tree = ElementTree(empty_root)
        self.svg.set_tree(empty_tree)

    def _update_svg_size(self):
        '''Update scaling instruction.
        Scale the svg to fill the entire button
        area, minus the padding area. Also set the 
        inverse sacling to prevent impacting downstream
        instructions. 
        '''
        svg_width, svg_height = self.svg.width, self.svg.height
        # Avoid divide by zero errors using short-circuiting logic
        x_sf = svg_width and (self.width - 2 * self.width_padding) / svg_width 
        y_sf = svg_height and (self.height - 2 * self.height_padding) / svg_height
        self.scale.xyz = x_sf, y_sf, 1
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