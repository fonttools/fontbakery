"""
Generate FontBakery's glyph_data.json file.

The glyph_data.json file contains the 'recommended' countour count for
encoded glyphs. The contour counts are derived from fonts which were
chosen for their quality and unique design decisions for particular glyphs.

Why make this?
Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only
be constructured in a handful of ways. This means a glyph's contour count
will only differ slightly amongst different fonts, e.g a 'g' could either
be 2 or 3 contours, depending on whether its double story or single story.
However, a quotedbl should have 2 contours, unless the font belongs to a
display family.

In the future, additional glyph data can be included. A good addition would
be the 'recommended' anchor counts for each glyph. Think of this file as a
glyph construction database.

"""
from __future__ import print_function
import os
import json
from fontTools.ttLib import TTFont

from fontbakery.utils import download_file, glyph_contour_count


class JsonSetEncoder(json.JSONEncoder):
    """Serialise Set objects for json module."""
    def default(self, obj):
       if isinstance(obj, set):
          return list(obj)
       return json.JSONEncoder.default(self, obj)


def get_font_data(font):
    font_data = []
    cmap = font['cmap'].getcmap(3,1).cmap
    cmap_reversed = dict(zip(cmap.values(), cmap.keys()))

    for glyph_name in font.getGlyphSet().keys():
        if glyph_name in cmap_reversed:
            uni_glyph = cmap_reversed[glyph_name]
            contours = glyph_contour_count(font, glyph_name)
            font_data.append({
                'unicode': uni_glyph,
                'name': glyph_name,
                'contours': set([contours])
            })
    return font_data


def collate_fonts_data(fonts_data):
    """Collate individual fonts data into a single glyph data file"""
    glyphs = {}

    for family in fonts_data:
        for glyph in family:
            if glyph['unicode'] not in glyphs:
                glyphs[glyph['unicode']] = glyph
            else:
                c = glyphs[glyph['unicode']]['contours']
                glyphs[glyph['unicode']]['contours'] = c | glyph['contours']
    return glyphs.values()


def main():

    git_ofl_prefix = 'http://github.com/google/fonts/raw/master/ofl/'
    git_ufl_prefix = 'http://github.com/google/fonts/raw/master/ufl/'
    git_apache_prefix = 'http://github.com/google/fonts/raw/master/apache/'

    fonts_urls = [
        git_ofl_prefix + 'sourceserifpro/SourceSerifPro-Bold.ttf',
        git_ofl_prefix + 'rosarivo/Rosarivo-Regular.ttf',
        git_ofl_prefix + 'raleway/Raleway-BlackItalic.ttf',
        git_ofl_prefix + 'librebaskerville/LibreBaskerville-Bold.ttf',
        git_ofl_prefix + 'worksans/WorkSans-Regular.ttf',
        git_ufl_prefix + 'ubuntu/Ubuntu-BoldItalic.ttf',
        git_ofl_prefix + 'vollkorn/Vollkorn-BlackItalic.ttf',
        git_ofl_prefix + 'breeserif/BreeSerif-Regular.ttf',
        git_ofl_prefix + 'carme/Carme-Regular.ttf',
        git_ofl_prefix + 'creteround/CreteRound-Regular.ttf',
        git_ofl_prefix + 'eczar/Eczar-Bold.ttf',
        git_ofl_prefix + 'faunaone/FaunaOne-Regular.ttf',
        git_ofl_prefix + 'hind/Hind-Light.ttf',
        git_ufl_prefix + 'ubuntumono/UbuntuMono-Bold.ttf',
        git_ofl_prefix + 'belgrano/Belgrano-Regular.ttf',
        git_ofl_prefix + 'trirong/Trirong-Light.ttf',
        git_ofl_prefix + 'mitr/Mitr-Regular.ttf',
        git_ofl_prefix + 'overpass/Overpass-Regular.ttf',
        git_ofl_prefix + 'jura/Jura-Regular.ttf',
        git_ofl_prefix + 'overpass/Overpass-Black.ttf',
        git_ofl_prefix + 'montserrat/Montserrat-Regular.ttf',
        git_ofl_prefix + 'montserrat/Montserrat-Black.ttf',
        git_ofl_prefix + 'montserrat/Montserrat-Thin.ttf',
        git_apache_prefix + 'roboto/Roboto-Regular.ttf',
    ]

    fonts_data = []
    for font_url in fonts_urls:
        print('Downloading and generating glyph data for {}'.format(font_url))
        font_ttf = download_file(font_url)
        font = TTFont(font_ttf)
        fonts_data.append(get_font_data(font))

    print('Collating font data into glyph data file')
    glyph_data = collate_fonts_data(fonts_data)

    script_path = os.path.dirname(__file__)
    glyph_data_path = os.path.join(script_path, '..', 'Lib', 'fontbakery', 'glyph_data.json')
    
    print('Saving to {}'.format(glyph_data_path))
    with open(glyph_data_path, 'w') as glyph_file:
        json.dump(glyph_data, glyph_file, indent=4, cls=JsonSetEncoder)
    print('done')


if __name__ == '__main__':
    main()
