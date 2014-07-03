import unittest
import mock
import simplejson
import StringIO


from checker.tests import test_check_canonical_filenames as tf_f
from checker.tests import test_check_canonical_styles as tf_s
from checker.tests import test_check_canonical_weights as tf_w
from checker.tests import test_check_familyname_matches_fontnames as tf_fm_eq
from checker.tests import test_check_menu_subset_contains_proper_glyphs as tf_subset
from checker.ttfont import Font as OriginFont


def _get_tests(TestCase):
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestCase)


def _run_font_test(TestCase):
    runner = unittest.TextTestRunner(stream=StringIO.StringIO())
    tests = _get_tests(TestCase)
    return runner.run(tests)


class Test_CheckCanonicalFilenamesTestCase(unittest.TestCase):

    @mock.patch.object(tf_f.CheckCanonicalFilenames, 'read_metadata_contents')
    def test_one(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family',
                'style': 'normal',
                'weight': 400,
                'filename': 'Family-Regular.ttf'
            }]
        })
        result = _run_font_test(tf_f.CheckCanonicalFilenames)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertEqual(result.failures, [])

        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family',
                'style': 'normal',
                'weight': 400,
                'filename': 'Family-Bold.ttf'
            }]
        })
        result = _run_font_test(tf_f.CheckCanonicalFilenames)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckCanonicalStyles(unittest.TestCase):

    @mock.patch.object(tf_s.CheckCanonicalStyles, 'read_metadata_contents')
    def test_two(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family',
                'style': 'normal',
                'weight': 400,
                'filename': 'Family-Regular.ttf'
            }]
        })

        class Font(object):
            macStyle = 0
            italicAngle = 0
            names = []

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = tf_s.ITALIC_MASK
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.macStyle = 0
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            mocked_get_ttfont.return_value.italicAngle = 10
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        class name:
            string = ''

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            n = name()
            n.string = 'italic'
            mocked_get_ttfont.return_value.names.append(n)
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckCanonicalWeights(unittest.TestCase):

    @mock.patch.object(tf_w.CheckCanonicalWeights, 'read_metadata_contents')
    def test_three(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'weight': 50
            }]
        })

        class Font(object):
            OS2_usWeightClass = 400

        # test if font weight less than 100 is invalid value
        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(tf_w.CheckCanonicalWeights)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        # test if font weight larger than 900 is invalid value
        metadata_contents.return_value = simplejson.dumps({
            'fonts': [{
                'weight': 901
            }]
        })

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = Font()
            result = _run_font_test(tf_w.CheckCanonicalWeights)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        # test if range 100..900 is valid values and checked for fonts
        for n in range(1, 10):
            with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
                mocked_get_ttfont.return_value = Font()
                metadata_contents.return_value = simplejson.dumps({
                    'fonts': [{
                        'weight': n * 100
                    }]
                })
                mocked_get_ttfont.return_value.OS2_usWeightClass = n * 100
                result = _run_font_test(tf_w.CheckCanonicalWeights)

            if result.errors:
                self.fail(result.errors[0][1])
            self.assertFalse(bool(result.failures))


class Test_CheckFamilyNameMatchesFontName(unittest.TestCase):

    @mock.patch.object(tf_fm_eq.CheckFamilyNameMatchesFontNames, 'read_metadata_contents')
    def test_four(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family'
            }]
        })
        result = _run_font_test(tf_fm_eq.CheckFamilyNameMatchesFontNames)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'FontName'
            }]
        })
        result = _run_font_test(tf_fm_eq.CheckFamilyNameMatchesFontNames)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))


class Test_CheckMenuSubsetContainsProperGlyphs(unittest.TestCase):

    @mock.patch.object(tf_subset.CheckMenuSubsetContainsProperGlyphs, 'read_metadata_contents')
    def test_five(self, metadata_contents):
        metadata_contents.return_value = simplejson.dumps({
            'name': 'Font Family',
            'fonts': [{
                'name': 'FontName',
                'filename': 'FontName-Regular.ttf'
            }]
        })

        class FontS:

            def retrieve_glyphs_from_cmap_format_4(self):
                return dict(map(lambda x: (ord(x), x), 'Font Name'))

        class FontF:

            def retrieve_glyphs_from_cmap_format_4(self):
                return dict(map(lambda x: (ord(x), x), 'FontName'))

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = FontS()
            result = _run_font_test(tf_subset.CheckMenuSubsetContainsProperGlyphs)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(OriginFont, 'get_ttfont') as mocked_get_ttfont:
            mocked_get_ttfont.return_value = FontF()
            result = _run_font_test(tf_subset.CheckMenuSubsetContainsProperGlyphs)
        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))
