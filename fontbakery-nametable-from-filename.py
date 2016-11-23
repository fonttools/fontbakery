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

MACSTYLE = {
    'Regular': 0,
    'Bold': 1,
    'Italic': 2,
    'Bold Italic': 3
}

# Weight name to value mapping:
WEIGHTS = {
    "Thin": 250,
    "ExtraLight": 275,
    "Light": 300,
    "Regular": 400,
    "Medium": 500,
    "SemiBold": 600,
    "Bold": 700,
    "ExtraBold": 800,
    "Black": 900
}

FSSELECTION = {
    'Regular': 64,
    'Italic': 1,
    'Bold': 32,
    'Bold Italic': 33,
    'UseTypoMetrics': 128
}


class GlyphsAppNameTable(object):
    """Convert a font's filename into a Glyphsapp name table schema.
    Glyphsapp v2.4.1 (942)
    """
    def __init__(self, filename, uniqueid, use_typo_metrics=False):
        self.filename = filename[:-4]
        self.family_name, self.style_name = self.filename.split('-')
        self.family_name = self._split_camelcase(self.family_name)
        self.uniqueid = uniqueid
        self.use_typo_metrics = use_typo_metrics

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
        name = self.style_name
        if name.startswith('Italic'):
            name = name
        elif 'Italic' in name:
            name = name.replace('Italic', ' Italic')
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
        else:
            return 'Regular'

    @property
    def unique_id(self):
        return ';'.join(self.uniqueid.split(';')[:-1]) + ';' + self.filename

    @property
    def full_name(self):
        name = '%s %s' % (self.family_name, self.style_name)
        if self.style_name.startswith('Italic'):
            name = name
        elif 'Italic' in self.style_name:
            name = name.replace('Italic', ' Italic')
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

    @property
    def weight(self):
        name = self.style_name
        if 'Italic' == self.style_name:
            name = 'Regular'
        elif 'Italic' in self.style_name:
            name = re.sub(r'Italic', r'', name)
        return WEIGHTS[name]

    @property
    def macstyle(self):
        return MACSTYLE[self.win_subfamily_name]

    @property
    def fsselection(self):
        if self.use_typo_metrics:
            f = FSSELECTION['UseTypoMetrics']
            return FSSELECTION[self.win_subfamily_name] + f
        return FSSELECTION[self.win_subfamily_name]

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


def typo_metrics_enabled(fsSelection):
    if fsSelection >= 128:
        return True
    return False


def swap_name(field, font_name_field, new_name):
    '''Replace a font's name field with a new name'''
    enc = font_name_field.getName(*field).getEncoding()
    text = str(font_name_field.getName(*field)).decode(enc)
    text = new_name
    font_name_field.setName(text, *field)


def main():
    args = parser.parse_args()

    for font_path in args.fonts:
        font_filename = ntpath.basename(font_path)
        font = TTFont(font_path)
        typo_enabled = typo_metrics_enabled(font)
        unique_id = str(font['name'].getName(3, 1, 0, 0))
        new_names = GlyphsAppNameTable(font_filename, unique_id, typo_enabled)

        for field in new_names:
            # Change name table
            if font['name'].getName(*field):
                swap_name(field, font['name'],
                          new_names[field])
        # Change OS/2 table
        font['OS/2'].usWeightClass = new_names.weight
        font['OS/2'].fsSelection = new_names.fsselection

        # Change head table
        font['head'].macStyle = new_names.macstyle

        font.save(font_path + '.fix')
        print 'font saved %s.fix' % font_path


if __name__ == '__main__':
    main()
