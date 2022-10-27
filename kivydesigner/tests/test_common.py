from kivydesigner.tests.common import KDGraphicUnitTest

class TestCommon(KDGraphicUnitTest):

    def test_screenshots_are_taken(self):
        '''
        Enabling the screenshots within the kivy testing framework requires
        the careful setting of environmental variables, so the screenshot
        functionality could be broken by moving an import statement. 

        Check that make_screenshots is set to True.
        '''
        from kivy.tests.common import make_screenshots
        assert make_screenshots
        # To-Do: I'm not sure if just checking this global is enough...
        # Maybe I can force a failure and then ignore it? try/render/except maybe..
