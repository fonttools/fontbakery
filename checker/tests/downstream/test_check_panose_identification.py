from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckPanoseIdentification(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    def test_check_panose_identification(self):
        font = Font.get_ttfont(self.path)

        values = {'bArmStyle': 0,
                  'bContrast': 0,
                  'bFamilyType': 0,
                  'bLetterForm': 0,
                  'bMidline': 0,
                  'bProportion': 0,
                  'bSerifStyle': 0,
                  'bStrokeVariation': 0,
                  'bWeight': 0,
                  'bXHeight': 0}.values()

        if font['OS/2'].panose.values() != values:
            self.fail('PANOSE should not be set to font')
