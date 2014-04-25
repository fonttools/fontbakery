import unittest


class ExampleTest(unittest.TestCase):

    def test_simple(self):
        self.assertFalse(False)

    def test_simple_coverage(self):
        from bakery.app import app
        self.assertEquals(app.config['DEBUG'], True)
