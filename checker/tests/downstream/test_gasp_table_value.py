from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckGaspTableType(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_check_gasp_table_type(self):
        """ Font table gasp should be 15 """
        font = Font.get_ttfont(self.path)
        try:
            font['gasp']
        except KeyError:
            self.fail('"GASP" table not found')

        if not isinstance(font['gasp'].gaspRange, dict):
            self.fail('GASP.gaspRange method value have wrong type')

        if 65535 not in font['gasp'].gaspRange:
            self.fail("GASP does not have 65535 gaspRange")

        # XXX: Needs review
        if font['gasp'].gaspRange[65535] != 15:
            self.fail('gaspRange[65535] value is not 15')

