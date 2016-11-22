import re

WIN_SAFE_STYLES = [
    'Regular',
    'Bold',
]


class GlyphsAppNameTable(object):
    """Convert a font's filename into a Glyphsapp name table schema.
    Glyphsapp v2.4.1 (942)
    """
    def __init__(self, filename, uniqueid):
        self.filename = filename[:-4]
        self. family_name, self.style_name = self.filename.split('-')
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
                return re.sub(r'Italic', '', name)
        return name

    @property
    def mac_subfamily_name(self):
        name = self.style_name
        if 'Italic' in name:
            name = re.sub('Italic', ' Italic', name)
        return name

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
        return ';'.join(self.uniqueid.split(';')[:-1]) + self.filename

    @property
    def full_name(self):
        name = self.filename.replace('-', ' ')
        if 'Italic' in self.filename:
            name = re.sub('Italic', ' Italic', name)
            return name
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


def main():
    font = 'Cabin-BlackItalic.ttf'
    font_names = GlyphsAppNameTable(font, '3.000;NeWT;Nunito-BoldItalic')
    print 'mac name: ', font_names.mac_family_name
    print 'win name: ', font_names.win_family_name

    print 'mac style: ', font_names.mac_subfamily_name
    print 'win style: ', font_names.win_subfamily_name
    print 'full name: ', font_names.full_name
    print 'ps name: ', font_names.postscript_name
    print 'pref fam name: ', font_names.pref_family_name
    print 'pref style name: ', font_names.pref_subfamily_name

    for i in font_names:
        print i, font_names[i]

if __name__ == '__main__':
    main()
