import unicodedata

from checker.base import BakeryTestCase as TestCase, tags
from cli.ttfont import Font


class CheckGlyphExistence(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def assertExists(self, d):
        font = Font.get_ttfont(self.path)
        glyphs = font.retrieve_cmap_format_4().cmap
        if not bool(ord(unicodedata.lookup(d)) in glyphs):
            self.fail('%s does not exist in font' % d)

    @tags('required')
    def test_nbsp(self):
        """ Check if 'NO-BREAK SPACE' exists in font glyphs """
        self.assertExists('NO-BREAK SPACE')

    @tags('required',)
    def test_space(self):
        """ Check if 'SPACE' exists in font glyphs """
        self.assertExists('SPACE')

    def test_euro(self):
        """ Check if 'EURO SIGN' exists in font glyphs """
        self.assertExists('EURO SIGN')
