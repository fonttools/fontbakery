"""Json reader for glyph data dictionaries and individual
glyph data dictionaries."""
import os
import json


def _glyph_data(json_file):
    """Load json glyph data files. Json should be structured in the
    following manner:
    [
        {
            "name": "endash",
            "unicode": 8211,
            "contours": [
                1
            ]
        },
        {
            "name": "emdash",
            "unicode": 8212,
            "contours": [
                1
            ]
        },
    ]

    "name" and "unicode "are compulsory keys which should be included in
    all glyph data files.

    "unicode" is an integer instead of a hex so it matches TTFont's cmap
    table key.
    """
    glyphs = {}
    with open(json_file, 'r') as glyph_data:
        glyph_data = json.loads(glyph_data.read())
        for glyph in glyph_data:
            glyphs[glyph['unicode']] = glyph
    return glyphs


path = os.path.dirname(__file__)

# The desired_glyph_data.json file contains the 'recommended' countour count
# for encoded glyphs. The contour counts are derived from fonts which were
# chosen for their quality and unique design decisions for particular glyphs.

# Why make this?
# Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only
# be constructured in a handful of ways. This means a glyph's contour count
# will only differ slightly amongst different fonts, e.g a 'g' could either
# be 2 or 3 contours, depending on whether its double story or single story.
# However, a quotedbl should have 2 contours, unless the font belongs to a
# display family.

# In the future, additional glyph data can be included. A good addition would
# be the 'recommended' anchor counts for each glyph.
desired_glyph_data_path = os.path.join(path, 'desired_glyph_data.json')
desired_glyph_data = _glyph_data(desired_glyph_data_path)
