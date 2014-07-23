from checker.base import BakeryTestCase as TestCase
from cli.ttfont import Font


class CheckFontNameEqualToMacStyleFlags(TestCase):

    path = '.'
    targets = ['result']
    name = __name__
    tool = 'lint'

    def test_fontname_is_equal_to_macstyle(self):
        """ Check that fontname is equal to macstyle flags """
        font = Font.get_ttfont(self.path)

        fontname = font.fontname
        macStyle = font.macStyle

        try:
            fontname_style = fontname.split('-')[1]
        except IndexError:
            self.fail(('Fontname is not canonical. Expected it contains '
                       'style. eg.: Italic, BoldItalic, Regular'))

        style = ''
        if macStyle & 0b01:
            style += 'Bold'

        if macStyle & 0b10:
            style += 'Italic'

        if not bool(macStyle & 0b11):
            style = 'Regular'

        if not fontname_style.endswith(style):
            _ = 'macStyle (%s) supposed style ended with "%s" but ends with "%s"'
            self.fail(_ % (bin(macStyle)[-2:], style, fontname_style))
