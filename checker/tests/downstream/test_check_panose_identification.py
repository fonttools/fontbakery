from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckPanoseIdentification(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_check_panose_identification(self):
        font = Font.get_ttfont(self.path)

        if font['OS/2'].panose['bProportion'] == 9:
            prev = 0
            for g in font.glyphs():
                if prev and font.advance_width(g) != prev:
                    link = ('http://www.thomasphinney.com/2013/01'
                            '/obscure-panose-issues-for-font-makers/')
                    self.fail(('Your font does not seem monospaced but PANOSE'
                               ' bProportion set to monospace. It may have '
                               ' a bug in windows. Details: %s' % link))
                prev = font.advance_width(g)
