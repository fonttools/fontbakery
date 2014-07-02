import unittest
import mock
import simplejson
import StringIO


from checker.tests import test_check_canonical_filenames as tests


def _get_tests(TestCase):
    return unittest.defaultTestLoader.loadTestsFromTestCase(TestCase)


def _run_font_test(TestCase):
    runner = unittest.TextTestRunner(stream=StringIO.StringIO())
    tests = _get_tests(TestCase)
    return runner.run(tests)


class Test_CheckCanonicalFilenamesTestCase(unittest.TestCase):

    @mock.patch.object(tests.CheckCanonicalFilenames, 'read_metadata_contents')
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
        result = _run_font_test(tests.CheckCanonicalFilenames)
        self.assertEqual(result.failures + result.errors, [])

        metadata_contents.return_value = simplejson.dumps({
            'name': 'Family',
            'fonts': [{
                'name': 'Family',
                'style': 'normal',
                'weight': 100,
                'filename': 'Family-Bold.ttf'
            }]
        })
        result = _run_font_test(tests.CheckCanonicalFilenames)
        self.assertTrue(bool(result.failures))
