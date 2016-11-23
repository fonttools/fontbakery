import re
import ntpath
import argparse
from argparse import RawTextHelpFormatter
from fontTools.ttLib import TTFont


description = """
Replace a collection of fonts nametable's with a new table based on the
filename and Glyphapp's naming schema.
"""

WIN_SAFE_STYLES = [
    'Regular',
    'Bold',
    'Italic',
    'BoldItalic',
]


class GlyphsAppNameTable(object):
    """Convert a font's filename into a Glyphsapp name table schema.
    Glyphsapp v2.4.1 (942)
    """
    def __init__(self, filename, uniqueid):
        self.filename = filename[:-4]
        self.family_name, self.style_name = self.filename.split('-')
        self.family_name = self._split_camelcase(self.family_name)
        self.uniqueid = uniqueid

    @property
    def mac_family_name(self):
        return self.family_name

    @property
    def win_family_name(self):
        name = self.family_name
        if self.style_name not in WIN_SAFE_STYLES:
            name = '%s %s' % (self.family_name, self.style_name)
        if 'Italic' in name:
            name = re.sub(r'Italic', r'', name)
        return name

    @property
    def mac_subfamily_name(self):
        return self._split_camelcase(self.style_name)

    @property
    def win_subfamily_name(self):
        name = self.style_name
        if 'BoldItalic' == name:
            return 'Bold Italic'
        elif 'Italic' in name:
            return 'Italic'
        elif name == 'Bold':
            return 'Bold'
        elif name == ' Regular':
            return 'Regular'

    @property
    def unique_id(self):
        return ';'.join(self.uniqueid.split(';')[:-1]) + ';' + self.filename

    @property
    def full_name(self):
        name = self.filename.replace('-', ' ')
        name = self._split_camelcase(name)
        return name

    @property
    def postscript_name(self):
        return self.filename

    @property
    def pref_family_name(self):
        return self.mac_family_name

    @property
    def pref_subfamily_name(self):
        return self.mac_subfamily_name

    def _split_camelcase(self, text):
        return re.sub(r"(?<=\w)([A-Z])", r" \1", text)

    def __dict__(self):
        # Mapping for fontTools getName method in the name table
        # nameID, platformID, platEncID, langID
        d = {
            # Mac
            (1, 1, 0, 0): self.mac_family_name,
            (2, 1, 0, 0): self.mac_subfamily_name,
            (3, 1, 0, 0): self.unique_id,
            (4, 1, 0, 0): self.full_name,
            (6, 1, 0, 0): self.postscript_name,
            # Win
            (1, 3, 1, 1033): self.win_family_name,
            (2, 3, 1, 1033): self.win_subfamily_name,
            (3, 3, 1, 1033): self.unique_id,
            (4, 3, 1, 1033): self.full_name,
            (6, 3, 1, 1033): self.postscript_name,
            (16, 3, 1, 1033): self.pref_family_name,
            (17, 3, 1, 1033): self.pref_subfamily_name
        }
        return d

    def __getitem__(self, key):
        return self.__dict__()[key]

    def __iter__(self):
        for i in self.__dict__():
            yield i


parser = argparse.ArgumentParser(description=description,
                                 formatter_class=RawTextHelpFormatter)
parser.add_argument('fonts', nargs="+")


def main():
    args = parser.parse_args()

    for font_path in args.fonts:
        font_filename = ntpath.basename(font_path)
        font = TTFont(font_path)
        unique_id = str(font['name'].getName(3, 1, 0, 0))
        new_names = GlyphsAppNameTable(font_filename, unique_id)

        for field in new_names:
            if font['name'].getName(*field):
                try:
                    field_enc = font['name'].getName(*field).getEncoding()
                    text = str(font['name'].getName(*field)).decode(field_enc)
                    text = new_names[field]
                    font['name'].setName(text, *field)
                except:
                    all
        font.save(font_path + '.fix')
        print 'font saved %s.fix' % font_path


if __name__ == '__main__':
    main()
