import os.path as op

from fontTools import ttLib


class Font(object):

    @staticmethod
    def get_ttfont(path, font_metadata, is_menu=False):
        path = op.join(op.dirname(path), font_metadata.filename)
        if is_menu:
            path = path.replace('.ttf', '.menu')
        return Font(path)

    def __init__(self, fontpath):
        self.ttfont = ttLib.TTFont(fontpath)

    @property
    def macStyle(self):
        return self.ttfont['head'].macStyle

    @property
    def italicAngle(self):
        return self.ttfont['post'].italicAngle

    @property
    def names(self):
        return self.ttfont['name'].names

    @property
    def OS2_usWeightClass(self):
        return self.ttfont['OS/2'].usWeightClass

    def retrieve_cmap_format_4(self):
        for cmap in self.ttfont['cmap'].tables:
            if cmap.format == 4:
                return cmap.cmap
