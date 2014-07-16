from checker.base import BakeryTestCase as TestCase
from checker.ttfont import Font
from checker.metadata import Metadata


class CheckVerticalMetrics(TestCase):

    targets = ['metadata']
    name = __name__
    path = '.'
    tool = 'lint'

    def read_metadata_contents(self):
        return open(self.path)

    def test_metrics_linegaps_are_zero(self):
        """ Check that linegaps in tables are zero """
        contents = self.read_metadata_contents()
        family_metadata = Metadata.get_family_metadata(contents)

        fonts_gaps_are_not_zero = []
        for font_metadata in family_metadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.path, font_metadata)
            if bool(ttfont.linegaps.os2typo) or bool(ttfont.linegaps.hhea):
                fonts_gaps_are_not_zero.append(font_metadata.filename)

        if fonts_gaps_are_not_zero:
            self.fail('%s have not zero linegaps' % fonts_gaps_are_not_zero)

    def test_metrics_ascents_equal_bbox(self):
        """ Check that ascents values are same as max glyph point """
        contents = self.read_metadata_contents()
        family_metadata = Metadata.get_family_metadata(contents)

        fonts_ascents_not_bbox = []
        ymax = 0

        _cache = {}
        for font_metadata in family_metadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.path, font_metadata)

            ymin_, ymax_ = ttfont.get_bbox()
            ymax = max(ymax, ymax_)

            _cache[font_metadata['filename']] = {
                'os2typo': ttfont.ascents.os2typo,
                'os2win': ttfont.ascents.os2win,
                'hhea': ttfont.ascents.hhea
            }

        for filename, data in _cache.items():
            if [data['os2typo'], data['os2win'], data['hhea']] != [ymax] * 3:
                fonts_ascents_not_bbox.append(filename)

        if fonts_ascents_not_bbox:
            _ = '%s ascents differ to max value: %s'
            self.fail(_ % (fonts_ascents_not_bbox, ymax))

    def test_metrics_descents_equal_bbox(self):
        """ Check that descents values are same as min glyph point """
        contents = self.read_metadata_contents()
        family_metadata = Metadata.get_family_metadata(contents)

        fonts_descents_not_bbox = []
        ymin = 0

        _cache = {}
        for font_metadata in family_metadata.fonts:
            ttfont = Font.get_ttfont_from_metadata(self.path, font_metadata)

            ymin_, ymax_ = ttfont.get_bbox()
            ymin = min(ymin, ymin_)

            _cache[font_metadata['filename']] = {
                'os2typo': ttfont.descents.os2typo,
                'os2win': ttfont.descents.os2win,
                'hhea': ttfont.descents.hhea
            }

        for filename, data in _cache.items():
            if [data['os2typo'], data['os2win'], data['hhea']] != [ymin] * 3:
                fonts_descents_not_bbox.append(filename)

        if fonts_descents_not_bbox:
            _ = '%s ascents differ to max value: %s'
            self.fail(_ % (fonts_descents_not_bbox, ymin))
