import magic
import os.path as op

from checker.base import BakeryTestCase as TestCase, tags
from checker.metadata import Metadata


class CheckFontsMenuAgreements(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path).read()

    def menufile(self, font_metadata):
        return '%s.menu' % font_metadata.post_script_name

    @tags('required')
    def test_menu_file_agreement(self):
        """ Check fonts have corresponding menu files """
        contents = self.read_metadata_contents()
        fm = Metadata.get_family_metadata(contents)
        for font_metadata in fm.fonts:
            menufile = self.menufile(font_metadata)
            path = op.join(op.dirname(self.path), menufile)

            if not op.exists(path):
                self.fail('%s does not exist' % menufile)

            if magic.from_file(path) != 'TrueType font data':
                self.fail('%s is not actual TTF file' % menufile)
