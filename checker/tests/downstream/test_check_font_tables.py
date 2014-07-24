from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckFontHasDsigTable(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_check_font_has_dsig_table(self):
        """ Check that font has DSIG table """
        font = Font.get_ttfont(self.path)
        try:
            font['DSIG']
        except KeyError:
            self.fail('Font does not have "DSIG" table')


class CheckFontHasNotKernTable(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_no_kern_table_exists(self):
        """ Check that no "KERN" table exists """
        font = Font.get_ttfont(self.path)
        try:
            font['KERN']
            self.fail('Font does not have "DSIG" table')
        except KeyError:
            pass
