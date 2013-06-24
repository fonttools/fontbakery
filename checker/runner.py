import sys, os
import argparse
import unittest
import StringIO

class BakeryRunner(object):
    pass

def make_suite(path):
    suite = unittest.TestSuite()
    # init block
    # declare tests here, don't forgot to init path

    from robofab_suite.openfolder import UfoOpenTest
    UfoOpenTest.path = path

    from fontforge_suite.fftest import SimpleTest
    SimpleTest.path = path

    # register block
    suite.addTests([
        unittest.defaultTestLoader.loadTestsFromTestCase(UfoOpenTest),
        # all other tests
        ])
    return suite

def run_suite(suite):
    buf = StringIO.StringIO()
    # XXX: here put own runner
    runner = unittest.TextTestRunner(buf)
    runner.run(suite)
    # on next step here will be runner object
    return buf.getvalue()

def run_set(path):
    """ Return tests results for .ufo font in parameter """
    assert os.path.exists(path)
    return run_suite(make_suite(path))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ufo', default='')
    # parser.add_argument('filename', default='')
    parser.add_argument('unittest_args', nargs='*')

    args = parser.parse_args()
    # #@$%
    s = make_suite(args.ufo)
    run_suite(s)
