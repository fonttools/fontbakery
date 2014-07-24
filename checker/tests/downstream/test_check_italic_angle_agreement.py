from checker.base import BakeryTestCase as TestCase, tags
from cli.ttfont import Font


class CheckItalicAngleAgreement(TestCase):

    path = '.'
    name = __name__
    targets = ['result']
    tool = 'lint'

    @tags('required')
    def test_check_italic_angle_agreement(self):
        """ Check italicangle property zero or negative """
        font = Font.get_ttfont(self.path)
        if font.italicAngle > 0:
            self.fail('italicAngle must be less or equal zero')
        if abs(font.italicAngle) > 20:
            self.fail('italicAngle can\'t be larger than 20 degrees')
