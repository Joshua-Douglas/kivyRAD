
import os 
import os.path
os.environ['KIVY_UNITTEST_SCREENSHOTS'] = '1'

from kivy.tests.common import GraphicUnitTest

class KDGraphicUnitTest(GraphicUnitTest):

    def expected_test_file_name(self):
        # Ancestor increments the cntr before generating each 
        # filename. Need to increment and decrement to calc name
        self.test_counter += 1
        test_uid = '%s-%d.png' % (
                '_'.join(self.id().split('.')[-2:]),
                self.test_counter)
        self.test_counter -= 1
        return os.path.join(self.results_dir, test_uid)

    def setUp(self):
        '''Override result directory to point to test_data.'''
        import os.path as path
        self.results_dir = path.join(path.dirname(__file__), 'test_data')
        super(KDGraphicUnitTest, self).setUp()