import unittest
import mock
import simplejson
import StringIO


from checker.tests import test_check_canonical_filenames as tf_f
from checker.tests import test_check_canonical_styles as tf_s


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

        with mock.patch.object(tf_s.Font, 'get_ttfont') as mock_method:
            mock_method.return_value = Font()
            mock_method.return_value.macStyle = tf_s.ITALIC_MASK
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))

        with mock.patch.object(tf_s.Font, 'get_ttfont') as mock_method:
            mock_method.return_value = Font()
            mock_method.return_value.macStyle = 0
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertFalse(bool(result.failures))

        with mock.patch.object(tf_s.Font, 'get_ttfont') as mock_method:
            mock_method.return_value = Font()
            mock_method.return_value.italicAngle = 10
            result = _run_font_test(tf_s.CheckCanonicalStyles)

        if result.errors:
            self.fail(result.errors[0][1])
        self.assertTrue(bool(result.failures))
