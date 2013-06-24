import unittest
import fontforge

class SimpleTest(unittest.TestCase):

    path = '.'

    def setUp(self):
        self.font = fontforge.open(self.path)

    def test_is_fsType_eq_n1(self):
        self.assertEqual(self.font.os2_fstype, -1)
