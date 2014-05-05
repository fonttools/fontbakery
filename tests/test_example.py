import unittest

from bakery.app import app


class ExampleTest(unittest.TestCase):

    def test_simple(self):
        self.assertFalse(False)

    def test_simple_coverage(self):
        self.assertEquals(app.config['DEBUG'], True)
