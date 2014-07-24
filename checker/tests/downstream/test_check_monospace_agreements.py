from checker.base import BakeryTestCase as TestCase
from checker.metadata import Metadata
from cli.ttfont import Font


class CheckMonospaceAgreement(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_check_monospace_agreement(self):
        """ Monospace font has hhea.advanceWidthMax equal to each
            glyph advanceWidth """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        if fm.category != 'Monospace':
            return
        for font_metadata in fm.fonts:
            font = Font.get_ttfont_from_metadata(self.path,
                                                 font_metadata.filename)
            prev = 0
            for g in font.glyphs():
                if prev and font.advance_width(g) != prev:
                    self.fail(('Glyph advanceWidth must be same'
                               ' across all glyphs %s' % prev))
                prev = font.advance_width(g)

            if prev != font.advance_width():
                msg = ('"hhea" table advanceWidthMax property differs'
                       ' to glyphs advanceWidth [%s, %s]')
                self.fail(msg % (prev, font.advance_width()))
