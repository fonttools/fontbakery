import fontforge

try:
    from checker.base import BakeryTestCase as TestCase
except ImportError:
    from unittest import TestCase


class SimpleTest(TestCase):

    path = '.'

    def setUp(self):
        self.font = fontforge.open(self.path)

    def test_is_fsType_eq_n1(self):
        self.assertEqual(self.font.os2_fstype, -1)
