import os.path as op
import unittest

from bakery.app import app
from bakery.tasks import get_subsets_coverage_data


class TaskTestCase(unittest.TestCase):

    def test_subsets_coverage_data(self):
        path = op.join(app.config['ROOT'], 'tests/fixtures/ttf/Font-Bold.ttf')
        self.assertTrue(get_subsets_coverage_data([path]))

        path = op.join(app.config['ROOT'], 'tests/fixtures/src/Font-Bold.ttx')
        self.assertTrue(get_subsets_coverage_data([path]))
