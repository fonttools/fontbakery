import os
import robofab.world
import robofab.objects

try:
    from checker.base import BakeryTestCase as TestCase
except ImportError:
    from unittest import TestCase


class UfoOpenTest(TestCase):

    path = '.'

    def setUp(self):
        self.font = robofab.world.OpenFont(self.path)
        # import ipdb; ipdb.set_trace()
        # print(self.path)

    def test_if_itis_exsist(self):
        """ This test check if file exists """
        self.assertEqual(os.path.exists(self.path), True)

    def test_is_ended_ufo(self):
        """ This test check do file name ends with .ufo"""
        self.assertEqual(self.path.lower().endswith('.ufo'), True)

    def test_is_it_folder(self):
        """ This test check if this is a folder"""
        self.assertEqual(os.path.isdir(self.path), True)

    def test_have_a(self):
        """ Do font have glyph named 'A' """
        self.assertTrue(self.font.has_key('A'))

    def test_failure(self):
        """ This test failed """
        self.assertTrue(False)

    def test_error(self):
        """ Unexpected error """
        1/0
        self.assertTrue(False)

    def test_a_is_glyph_instanse(self):
        """ Do font property A is proper type object """
        if self.font.has_key('A'):
            a = self.font['A']
        else:
            a = None
        self.assertIsInstance(a, robofab.objects.objectsRF.RGlyph)

    def test_is_fsType_eq_1(self):
        pass

