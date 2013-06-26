import sys, os
import argparse
import unittest
import StringIO

class BakeryTestResult(unittest.TestResult):

    def __init__(self, stream=None, descriptions=None, verbosity=None,
            success_list=None, error_list=None, failure_list=None):
        self.sl = success_list
        self.el = error_list
        self.fl = failure_list
        super(BakeryTestResult, self).__init__(self)

    def startTest(self, test):
        super(BakeryTestResult, self).startTest(test)

    def addSuccess(self, test):
        super(BakeryTestResult, self).addSuccess(test)
        if hasattr(self.sl, 'append'):
            self.sl.append(test)

    def addError(self, test, err):
        super(BakeryTestResult, self).addError(test, err)
        if hasattr(self.el, 'append'):
            self.el.append(test)

    def addFailure(self, test, err):
        super(BakeryTestResult, self).addFailure(test, err)
        if hasattr(self.fl, 'append'):
            self.fl.append(test)

class BakeryTestRunner(unittest.TextTestRunner):
    def __init__(self, descriptions=True, verbosity=1, resultclass=None,
            success_list=None, error_list=None, failure_list=None):

        self.sl = success_list
        self.el = error_list
        self.fl = failure_list

        self.results = []
        self.descriptions = descriptions
        self.verbosity = verbosity
        if resultclass is not None:
            self.resultclass = resultclass
        super(BakeryTestRunner, self).__init__(self)

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions,
            self.verbosity, self.sl, self.el, self.fl)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        test(result)
        self.results.append(result)
        return result

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
    result = {
        'success': [],
        'error': [],
        'failure': []
    }
    runner = BakeryTestRunner(resultclass = BakeryTestResult,
        success_list=result['success'], error_list=result['error'],
        failure_list=result['failure'])
    runner.run(suite)
    result['sum'] = sum(map(len, [result[x] for x in result.keys() ]))

    # on next step here will be runner object
    return result

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
