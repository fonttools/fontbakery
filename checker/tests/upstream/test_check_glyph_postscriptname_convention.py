import re

from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckPostscriptnameGlyphConventions(TestCase):

    path = '.'
    name = __name__
    targets = ['upstream-ttx']
    tool = 'lint'

    def test_Check_Postscriptname_Glyph_Conventions(self):
        """ Check glyphs names comply with PostScript conventions """
        font = Font.get_ttfont(self.path)
        for glyph in font.glyphs():
            if glyph == '.notdef':
                continue
            if not re.match('(^[.0-9])[a-zA-Z_][a-zA-Z_0-9]{,30}', glyph):
                self.fail(('Glyph "%s" does not comply conventions.'
                           ' A glyph name may be up to 31 characters in length,'
                           ' must be entirely comprised of characters from'
                           ' the following set:'
                           ' A-Z a-z 0-9 .(period) _(underscore). and must not'
                           ' start with a digit or period. The only exception'
                           ' is the special character ".notdef". "twocents",'
                           ' "a1", and "_" are valid glyph names. "2cents"'
                           ' and ".twocents" are not.'))
