import os.path as path
from pathlib import Path

from kivy.lang.builder import Builder
from kivydesigner.uix.iconbutton import IconButton
from kivydesigner.tests.common import KDGraphicUnitTest, TEST_DATA_DIR

class TestIconButton(KDGraphicUnitTest):

    def test_no_svg(self):
        '''Test that an icon button without any svg image 
        looks just like a normal button.  
        '''
        self.render(IconButton(text='No SVG here...'))

    def test_load_svg_kv(self):
        '''Test that the SVG button can load reasonably complex
        images, using kvlang creation.
        '''
        svg_file = path.join(TEST_DATA_DIR, 'pumk.svg')
        # Force forward slash for kvlang
        svg_file = Path(svg_file).as_posix()
        ex_kv = f'''
BoxLayout:
    Button:
        text: 'first'
    IconButton:
        source: "{svg_file}"
        text: "hidden"
    Button:
        text: 'second'
    '''
        root = Builder.load_string(ex_kv)
        self.render(root)

    def test_load_svg_obj(self):
        '''Test that the SVG button can load reasonably complex
        images, using object creation.
        '''
        svg_file = path.join(TEST_DATA_DIR, 'pumk.svg')
        root = IconButton()
        root.source = svg_file
        self.render(root)

    def test_padding(self):
        '''Test that the SVG button width padding and height padding
        add spacing between the SVG and the edge of the button. 
        '''
        svg_file = path.join(TEST_DATA_DIR, 'blue.svg')
        root = IconButton()
        root.source = svg_file
        # Test without padding
        self.render(root)
        # Test only height padding
        root.svg_padding_y = 250 
        root.svg_padding_x = 0
        self.render(root)
        # Test only width padding 
        root.svg_padding_x = 150 
        root.svg_padding_y = 0
        self.render(root)
        # Test both padding 
        root.svg_padding = (70, 170)
        self.render(root)

    def test_padding_edge_cases(self):
        '''Test nontraditonal padding values supported by 
        the IconButton. Negative paddings will
        stretch the svg. Padding values greater than the 
        length will invert the image.
        '''
        svg_file = path.join(TEST_DATA_DIR, 'pumk.svg')
        root = IconButton()
        root.source = svg_file
        root.svg_padding = (-100, -200)
        # Expect stretched pumpkin 
        self.render(root)
        root.svg_padding = (root.width+75, root.height+75)
        # Expect inverted image
        self.render(root)

    def test_app(self):
        from kivy.app import App
        self.render(App())