import os
import json


def _glyph_data(json_file):
    glyphs = {}
    with open(json_file, 'r') as glyph_data:
        glyph_data = json.loads(glyph_data.read())
        for glyph in glyph_data:
            glyphs[glyph['unicode']] = glyph
    return glyphs


path = os.path.dirname(__file__)


desired_glyph_data_path = os.path.join(path, 'glyph_data.json')
desired_glyph_data = _glyph_data(desired_glyph_data_path)
