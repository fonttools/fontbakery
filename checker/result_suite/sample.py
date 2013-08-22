from checker.base import BakeryTestCase as TestCase

class SampleTest(TestCase):
    target = 'result'

    path = '.'

    def setUp(self):
        # read ttf
        # self.font = fontforge.open(self.path)
        pass

    def test_ok(self):
<<<<<<< HEAD
        """ This test succeeds """
        self.assertTrue(True)

    def test_failure(self):
        """ This test fails """
=======
        """ This test failed """
        self.assertTrue(True)

    def test_failure(self):
        """ This test failed """
>>>>>>> 1eb7b6e65b0c48cd3ef369741d0be18823a1eea7
        self.assertTrue(False)

    def test_error(self):
        """ Unexpected error """
        1 / 0
        self.assertTrue(False)
