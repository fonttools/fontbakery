from checker.base import BakeryTestCase as TestCase
from checker.ttfont import Font


class CheckOS2WidthClass(TestCase):

    path = '.'
    targets = ['result']
    name = __name__
    tool = 'lint'

    def test_check_os2_width_class(self):
        font = Font.get_ttfont(self.path)
        error = "OS/2 widthClass must be [1..9] inclusive, was %s IE9 fail"
        error = error % font.OS2_usWidthClass
        self.assertIn(font.OS2_usWidthClass, range(1, 10), error)
