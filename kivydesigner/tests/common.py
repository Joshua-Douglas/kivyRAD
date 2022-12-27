
import os 
import shutil
import os.path as path
os.environ['KIVY_UNITTEST_SCREENSHOTS'] = '1'
import pytest

from kivy.tests.common import GraphicUnitTest

TEST_DATA_DIR = path.join(path.dirname(__file__), 'test_data')
TMP_DATA_DIR = path.join(path.dirname(__file__), 'test_output')

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
        self.results_dir = TEST_DATA_DIR
        super(KDGraphicUnitTest, self).setUp()

@pytest.fixture
def test_output_dir():
    '''Fixture to create a test output directory.
    Cleanup all created files after test.
    '''
    os.mkdir(TMP_DATA_DIR)
    yield TMP_DATA_DIR
    shutil.rmtree(TMP_DATA_DIR)