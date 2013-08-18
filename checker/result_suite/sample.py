from checker.base import BakeryTestCase as TestCase

class SampleTest(TestCase):

    path = '.'

    def setUp(self):
        # read ttf
        # self.font = fontforge.open(self.path)
        pass

    def test_ok(self):
        """ This test failed """
        self.assertTrue(True)

    def test_failure(self):
        """ This test failed """
        self.assertTrue(False)

    def test_error(self):
        """ Unexpected error """
        1 / 0
        self.assertTrue(False)
