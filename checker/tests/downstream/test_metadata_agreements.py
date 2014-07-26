import os

from checker.base import BakeryTestCase as TestCase, tags
from checker.metadata import Metadata
from cli.ttfont import Font


class CheckMetadataAgreements(TestCase):

    path = '.'
    name = __name__
    targets = ['metadata']
    tool = 'lint'

    def setUp(self):
        contents = self.read_metadata_contents()
        self.metadata = Metadata.get_family_metadata(contents)

    def read_metadata_contents(self):
        return open(self.path).read()

    def test_metadata_family_values_are_all_the_same(self):
        """ Check that METADATA family values are all the same """
        name = ''
        for font_metadata in self.metadata.fonts:
            if name and font_metadata.name != name:
                self.fail('Family name in metadata fonts items not the same')
            name = font_metadata.name

    @tags('required',)
    def test_metadata_family(self):
        """ Font and METADATA.json have the same name """
        for font_metadata in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.path, font_metadata)
            if font.familyname != font_metadata.name:
                msg = 'Family name in TTF is "%s" but in METADATA "%s"'
                self.fail(msg % (font.familyname, font_metadata.name))

    def test_metadata_font_have_regular(self):
        """ According GWF standarts font should have Regular style. """
        # this tests will appear in each font
        have = False
        for i in self.metadata.fonts:
            if i.full_name.endswith('Regular'):
                have = True

        self.assertTrue(have)

    @tags('required',)
    def test_metadata_regular_is_400(self):
        """ Usually Regular should be 400 """
        have = False
        for i in self.metadata.fonts:
            if i.fullname.endswith('Regular') and i.weight == 400:
                have = True

        self.assertTrue(have)

    def test_metadata_regular_is_normal(self):
        """ Usually Regular should be normal style """
        have = False
        for x in self.metadata.fonts:
            if x.full_name.endswith('Regular') and x.style == 'normal':
                have = True
        self.assertTrue(have)

    @tags('required')
    def test_metadata_filename_matches_postScriptName(self):
        """ METADATA.json `filename` matches `postScriptName` """
        for x in self.metadata.fonts:
            post_script_name = x.post_script_name
            filename = x.full_name
            self.assertEqual(os.path.splitext(filename)[0], post_script_name)

    @tags('required')
    def test_metadata_fullname_matches_postScriptName(self):
        """ METADATA.json `fullName` matches `postScriptName` """
        for x in self.metadata.fonts:
            post_script_name = x.post_script_name.replace('-', ' ')
            fullname = x.full_name
            self.assertEqual(fullname, post_script_name)

    @tags('required')
    def test_metadata_postScriptName_matches_ttf_fontname(self):
        """ Checks METADATA.json 'postScriptName' matches TTF 'postScriptName' """
        for font_metadata in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.path, font_metadata)
            self.assertEqual(font.post_script_name,
                             font_metadata.post_script_name)

    def test_metadata_fullname_is_equal_to_internal_font_fullname(self):
        """ METADATA.json 'fullname' value matches internal 'fullname' """
        for font_metadata in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.path, font_metadata)
            self.assertEqual(font.fullname, font_metadata.full_name)

    def test_font_name_matches_family(self):
        """ METADATA.json fonts 'name' property should be
            same as font familyname """

        for font_metadata in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.path, font_metadata)
            if font_metadata.name != font.familyname:
                msg = '"fonts.name" property is not the same as TTF familyname'
                self.fail(msg)

    def test_metadata_fonts_fields_have_fontname(self):
        """ METADATA.json fonts items fields "name", "postScriptName",
            "fullName", "filename" contains font name right format """
        for x in self.metadata.fonts:
            font = Font.get_ttfont_from_metadata(self.path, x)

            self.assertIn(font.familyname, x.name)
            self.assertIn(font.familyname, x.full_name)
            self.assertIn("".join(str(font.familyname).split()),
                          x.filename)
            self.assertIn("".join(str(font.familyname).split()),
                          x.post_script_name)
