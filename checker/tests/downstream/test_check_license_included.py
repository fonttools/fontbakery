import re

from checker.base import BakeryTestCase as TestCase, tags
from cli.ttfont import Font


class CheckLicenseIncluded(TestCase):

    path = '.'
    targets = 'result'
    name = __name__
    tool = 'lint'

    @tags('required')
    def test_license_included_in_font_names(self):
        font = Font.get_ttfont(self.path)

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not regex.match(font.license_url):
            self.fail("LicenseUrl is required and must be correct url")
