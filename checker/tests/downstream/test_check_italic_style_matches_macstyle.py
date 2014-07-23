from checker.base import BakeryTestCase as TestCase
from checker.metadata import Metadata
from cli.ttfont import Font


class CheckItalicStyleMatchesMacStyle(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_check_italic_style_matches_mac_style(self):
        """ Check metadata.json font.style `italic` matches font internal """
        contents = self.read_metadata_contents()
        family = Metadata.get_family_metadata(contents)

        for font_metadata in family.fonts:
            if font_metadata.style != 'italic':
                continue

            font = Font.get_ttfont_from_metadata(self.path, font_metadata)

            if not bool(font.macStyle & 0b10):
                self.fail(('Metadata style has been set to italic'
                           ' but font second bit in macStyle has'
                           ' not been set'))

            style = font.familyname.split('-')[-1]
            if not style.endswith('Italic'):
                self.fail(('macStyle second bit is set but postScriptName "%s"'
                           ' is not ended with "Italic"') % font.familyname)

            style = font.fullname.split('-')[-1]
            if not style.endswith('Italic'):
                self.fail(('macStyle second bit is set but fullName "%s"'
                           ' is not ended with "Italic"') % font.fullname)
