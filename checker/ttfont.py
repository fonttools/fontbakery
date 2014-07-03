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

    @property
    def familyname(self):
        windows_entry = None

        for entry in self.names:
            if entry.nameID != 6:
                continue
            # macintosh platform
            if entry.platformID == 1 and entry.langID == 0:
                return Font.bin2unistring(entry)
            if entry.platformID == 3 and entry.langID == 0x409:
                windows_entry = entry

        return windows_entry

    def retrieve_cmap_format_4(self):
        for cmap in self.ttfont['cmap'].tables:
            if cmap.format == 4:
                return cmap.cmap

    def advanceWidth(self, glyph_id):
        try:
            return self.ttfont['hmtx'].metrics[glyph_id][0]
        except KeyError:
            return None

    @staticmethod
    def bin2unistring(record):
        if b'\000' in record.string:
            string = record.string.decode('utf-16-be')
            return string.encode('utf-8')
        else:
            return record.string
