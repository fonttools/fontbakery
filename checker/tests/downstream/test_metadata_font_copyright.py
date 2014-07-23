from checker.base import BakeryTestCase as TestCase, tags
from checker.metadata import Metadata


class CheckMetadataContainsReservedFontName(TestCase):

    path = '.'
    targets = 'metadata'
    name = __name__
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    @tags(['required', 'info'])
    def test_postscriptname_contains_correct_weight(self):
        """ Metadata weight matches postScriptName """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:

            if 'Reserved Font Name' not in font_metadata.copyright:
                msg = '"%s" should have "Reserved File Name"'
                self.fail(msg % font_metadata.copyright)

    @tags('required')
    def test_copyright_matches_pattern(self):
        """ Copyright string matches to Copyright * 20\d\d * (*@*.*) """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)

        for font_metadata in fm.fonts:
            self.assertRegexpMatches(font_metadata.copyright,
                                     r'Copyright\s+\(c\)\s+20\d{2}.*\(.*@.*.*\)')
