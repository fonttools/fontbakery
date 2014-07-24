import magic
import os

from checker.base import BakeryTestCase as TestCase, tags
from cli.ttfont import Font


class CheckFontAgreements(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def setUp(self):
        self.font = Font.get_ttfont(self.path)

    @tags('required')
    def test_em_is_1000(self):
        """ Font em should be equal 1000 """
        self.assertEqual(self.font.get_upm_height(), 1000)

    @tags('required')
    def test_is_fsType_not_set(self):
        """Is the OS/2 table fsType set to 0?"""
        self.assertEqual(self.font.OS2_fsType, 0)

    @tags('required')
    def test_latin_file_exists(self):
        """ Check latin subset font file exists """
        self.assertTrue(os.path.exists("%s.latin" % self.fname))

    @tags('required')
    def test_file_is_font(self):
        """ Menu file have font-name-style.menu format """
        self.assertTrue(magic.from_file(self.path), 'TrueType font data')

    @tags('required')
    def test_font_is_font(self):
        """ File provided as parameter is TTF font file """
        self.assertTrue(magic.from_file(self.path, mime=True),
                        'application/x-font-ttf')
