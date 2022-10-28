from kivy.lang.builder import Builder
from kivydesigner.tests.common import KDGraphicUnitTest

class TestIconButton(KDGraphicUnitTest):

    def test_no_svg(self):
        '''Test that an icon button without any svg image 
        looks just like a normal button.  
        '''
        ex_kv = r'''
BoxLayout:
    Button:
        text: 'first'
    IconButton:
        text: "hidden"
        svg_padding: 25, 50
    Button:
        text: 'second'
    '''
        root = Builder.load_string(ex_kv)
        self.render(root)