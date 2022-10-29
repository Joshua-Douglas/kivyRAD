from kivydesigner.tests.common import KDGraphicUnitTest
from kivy.uix.button import Button

class TestCommon(KDGraphicUnitTest):

    def test_screenshots_are_taken(self):
        '''
        Enabling the screenshots within the kivy testing framework requires
        the careful setting of environmental variables, so the screenshot
        functionality could be broken by moving an import statement. 
        '''
        from kivy.tests.common import make_screenshots
        assert make_screenshots

        # Test data contains a snapshot that we know does not
        # looks like this. If self.render fails to compare the
        # snapshot then self.test_failed will be False after 
        # render returns. 
        root = Button(text='Screenshot def does not look like this')
        self.render(root)
        assert self.test_failed
        self.test_failed = False
