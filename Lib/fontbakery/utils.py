#!/usr/bin/env python3
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import sys

from fontTools.ttLib import TTFont
from typing import Text, Optional
from fontbakery.constants import NO_COLORS_THEME, DARK_THEME, LIGHT_THEME
from vharfbuzz import Vharfbuzz



# TODO: this should be part of FontBakeryCheck and check.conditions
# should be a tuple (negated, name)
def is_negated(name):
    stripped = name.strip()
    if stripped.startswith('not '):
        return True, stripped[4:].strip()
    if stripped.startswith('!'):
        return True, stripped[1:].strip()
    return False, stripped


def colorless_len(str):
    import re
    return len(re.sub('\x1b(\\[[0-9;]+|\\].+)m', '', str))

def text_flow(content, width=80, indent=0, left_margin=0, first_line_indent=0,
              space_padding=False, text_color="{}".format):
    result = []
    line_num = 0
    for line in content.split("\n"):
        _indent = indent
        _width = width

        if line.strip() == "":
            if space_padding:
                result.append(" " * _indent + text_color(" " * _width))
            continue

        words = line.split(" ")
        while words:
            line_num += 1
            if line_num == 1:
                if left_margin > -first_line_indent:
                    inside_indent = " " * (left_margin + first_line_indent)
                else:
                    inside_indent = ""
            else:
                inside_indent = " " * left_margin
            this_line = inside_indent + words.pop(0)

            if colorless_len(this_line) > _width:
                # let's see what we can do to make it fit
                if "/" in this_line:
                    # here we feed-back chunks of a URL
                    # into words if it overflows the block
                    chunks = this_line.split('/')
                    new_line = chunks.pop(0)
                    while chunks:
                        next_len = colorless_len(new_line) + 1 + colorless_len(chunks[0])
                        if next_len >= _width: break
                        new_line += "/" + chunks.pop(0)
                    this_line = new_line
                    words.insert(0, "/" + "/".join(chunks))
                else:
                    # not sure what else to do,
                    # so we'll simply cut the long word
                    words.insert(0, this_line[_width:])
                    this_line = this_line[:_width]

            while words and (colorless_len(this_line) + 1 + colorless_len(words[0]) <= width):
                this_line += " " + words.pop(0)

            if space_padding:
                # pad the line with spaces to fit the block width:
                this_line += " " * (_width - colorless_len(this_line))
            result.append(" " * _indent + text_color(this_line))
    return "\n".join(result)


def get_theme(args):
    if args.no_colors:
        return NO_COLORS_THEME
    if args.light_theme:
        return LIGHT_THEME
    if args.dark_theme:
        return DARK_THEME
    if sys.platform == "darwin":
        # The vast majority of MacOS users seem to use a light-background on the text terminal
        return LIGHT_THEME
    # For orther systems like GNU+Linux and Windows, a dark terminal seems to be more common.
    return DARK_THEME


def unindent_rationale(rationale, checkid=None):
    content = ""
    for line in rationale.split("\n"):
        if line.strip() == "":
            content += "\n"
            continue

        # all lines are assumed to be indented by 8 spaces
        content += line[8:] + "\n"
    return content


def split_camel_case(camelcase):
    result = []
    word = ""
    for char in camelcase:
        if char.isupper():
            if word != "":
                result.append(word)
            word = char
        else:
            word += char

    if word != "":
        result.append(word)
    return " ".join(result)


def suffix(font):
    filename = os.path.basename(font)
    basename = os.path.splitext(filename)[0]
    s = basename.split('-')
    s.pop(0)
    return '-'.join(s)


def pretty_print_list(values, shorten=10, sep=", ", glue="and"):
    if len(values) == 1:
        return str(values[0])

    if shorten and len(values) > shorten + 2:
        return "{} {} {} more.".format(sep.join(map(str, values[:shorten])),
                                       glue,
                                       len(values) - shorten)
    else:
        return "{} {} {}".format(sep.join(map(str, values[:-1])),
                                 glue,
                                 str(values[-1]))


def bullet_list(values, bullet="-"):
    return f" {bullet} " + pretty_print_list(values,
                                             shorten=False,
                                             sep=f"\n {bullet} ",
                                             glue=f"\n {bullet}")

def get_regular(fonts):
    # TODO: Maybe also support getting a regular instance from a variable font?
    for font in fonts:
        if "-Regular.ttf" in font:
            return font


def get_absolute_path(p):
    if os.path.isabs(p):
        abspath = p
    else:
        abspath = os.path.join(os.path.abspath('.'), p)
    return abspath


def filesize_formatting(s):
    if s < 1024:
        return f"{s} bytes"
    elif s < 1024*1024:
        return "{:.1f}kb".format(s/1024)
    else:
        return "{:.1f}Mb".format(s/(1024*1024))


def get_bounding_box(font):
    """ Returns max and min bbox of given truetype font """
    ymin = 0
    ymax = 0
    if font.sfntVersion == 'OTTO':
        ymin = font['head'].yMin
        ymax = font['head'].yMax
    else:
        for g in font['glyf'].glyphs:
            char = font['glyf'][g]
            if hasattr(char, 'yMin') and ymin > char.yMin:
                ymin = char.yMin
            if hasattr(char, 'yMax') and ymax < char.yMax:
                ymax = char.yMax
    return ymin, ymax


def get_name_entries(font,
                     nameID,
                     platformID=None,
                     encodingID=None,
                     langID=None):
    results = []
    for entry in font['name'].names:
        if entry.nameID == nameID and \
           (platformID is None or entry.platformID == platformID) and \
           (encodingID is None or entry.platEncID == encodingID) and \
           (langID is None or entry.langID == langID):
            results.append(entry)
    return results


def get_name_entry_strings(font,
                           nameID,
                           platformID=None,
                           encodingID=None,
                           langID=None):
    entries = get_name_entries(font, nameID, platformID, encodingID, langID)
    return list(map(lambda e: e.string.decode(e.getEncoding()), entries))


def name_entry_id(name):
    from fontbakery.constants import (NameID,
                                      PlatformID)
    return "[{}({}):{}({})]".format(NameID(name.nameID).name,
                                    name.nameID,
                                    PlatformID(name.platformID).name,
                                    name.platformID)


def get_glyph_name(font: TTFont, codepoint: int) -> Optional[str]:
    next_best_cmap = font.getBestCmap()

    if codepoint in next_best_cmap:
        return next_best_cmap[codepoint]

    return None


def glyph_contour_count(font, name):
    """Contour count for specified glyph.
    This implementation will also return contour count for
    composite glyphs.
    """
    contour_count = 0
    items = [font['glyf'][name]]

    while items:
        g = items.pop(0)
        if g.isComposite():
            for comp in g.components:
                if comp.glyphName != ".ttfautohint":
                    items.append(font['glyf'][comp.glyphName])
        if g.numberOfContours != -1:
            contour_count += g.numberOfContours
    return contour_count


def get_font_glyph_data(font):
    """Return information for each glyph in a font"""
    from fontbakery.constants import (PlatformID,
                                      WindowsEncodingID)
    font_data = []

    try:
        subtable = font['cmap'].getcmap(PlatformID.WINDOWS,
                                        WindowsEncodingID.UNICODE_BMP)
        if not subtable:
                    # Well... Give it a chance here...
                    # It may be using a different Encoding_ID value
            subtable = font['cmap'].tables[0]

        cmap = subtable.cmap
    except:
        return None

    cmap_reversed = dict(zip(cmap.values(), cmap.keys()))

    for glyph_name in font.getGlyphSet().keys():
        if glyph_name in cmap_reversed:
            uni_glyph = cmap_reversed[glyph_name]
            contours = glyph_contour_count(font, glyph_name)
            font_data.append({
                'unicode': uni_glyph,
                'name': glyph_name,
                'contours': {contours}
            })
    return font_data

def get_Protobuf_Message(klass, path):
    from google.protobuf import text_format
    message = klass()
    text_data = open(path, "rb").read()
    text_format.Merge(text_data, message)
    return message

def get_FamilyProto_Message(path):
    from fontbakery.fonts_public_pb2 import FamilyProto
    return get_Protobuf_Message(FamilyProto, path)

def get_DesignerInfoProto_Message(text_data):
    from fontbakery.designers_pb2 import DesignerInfoProto
    from google.protobuf import text_format
    message = DesignerInfoProto()
    text_format.Merge(text_data, message)
    return message

def check_bit_entry(ttFont, table, attr, expected, bitmask, bitname):
    from fontbakery.message import Message
    from fontbakery.status import (PASS, FAIL)
    value = getattr(ttFont[table], attr)
    name_str = f"{table} {attr} {bitname} bit"
    if bool(value & bitmask) == expected:
        return PASS, f"{name_str} is properly set."
    else:
        if expected:
            expected_str = "set"
        else:
            expected_str = "unset"
        return FAIL,\
               Message(f"bad-{bitname}",
                       f"{name_str} should be {expected_str}.")


class BadCertificateSetupException(Exception):
    pass


def download_file(url):
    from urllib.request import urlopen
    from urllib.error import URLError
    from io import BytesIO
    try:
        return BytesIO(urlopen(url).read())
    except URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e.reason):
            raise BadCertificateSetupException(
                "You probably installed official"
                " Mac python from python.org but forgot to also install"
                " the certificates. There is a note in the installer"
                " Readme about that. Check the Python folder in the"
                " Applications directory, you should find a shell script"
                " to install the certificates.")


def cff_glyph_has_ink(font: TTFont, glyph_name: Text) -> bool:
    if 'CFF2' in font:
        top_dict = font['CFF2'].cff.topDictIndex[0]
    else:
        top_dict = font['CFF '].cff.topDictIndex[0]
    char_strings = top_dict.CharStrings
    char_string = char_strings[glyph_name]
    bounds = char_string.calcBounds(char_strings)
    if bounds is not None:
        return True

    return False


def ttf_glyph_has_ink(font: TTFont, name: Text) -> bool:
    glyph = font['glyf'].glyphs[name]
    glyph.expand(font['glyf'])

    if not glyph.isComposite():
        if glyph.numberOfContours == 0:
            return False
        (coords, _, _) = glyph.getCoordinates(font['glyf'])
        # you need at least 3 points to draw
        return len(coords) > 2

    # Check for ink in each sub-component.
    for glyph_name in glyph.getComponentNames(glyph.components):
        if glyph_has_ink(font, glyph_name):
            return True

    return False


def unicoderange_bit_name(bit):
    from fontbakery.constants import UNICODERANGE_DATA
    return UNICODERANGE_DATA[bit][0][1]


def get_preferred_cmap(ttFont):
    cmaps = {}
    for table in ttFont["cmap"].tables:
        cmaps[table.format] = table.cmap

    if 12 in cmaps:
        return cmaps[12]

    elif 4 in cmaps:
        return cmaps[4]

    else:
        return None


def chars_in_range(ttFont, bit):
    from fontbakery.constants import UNICODERANGE_DATA
    cmap = get_preferred_cmap(ttFont)
    chars = []
    for c in sorted(cmap):
        for entry in UNICODERANGE_DATA[bit]:
            if c >= entry[2] and c <= entry[3]:
                chars.append(c)
    return chars


def compute_unicoderange_bits(ttFont):
    from fontbakery.constants import UNICODERANGE_DATA
    cmap = get_preferred_cmap(ttFont)
    result = 0
    for c in sorted(cmap):
        for bit in range(len(UNICODERANGE_DATA)):
            for entry in UNICODERANGE_DATA[bit]:
                bit = entry[0]
                if c >= entry[2] and c <= entry[3]:
                    result |= (1 << bit)
    return result


def glyph_has_ink(font: TTFont, name: Text) -> bool:
    """Checks if specified glyph has any ink.

    That is, that it has at least one defined contour associated.
    Composites are considered to have ink if any of their components have ink.
    Args:
        font:       the font
        glyph_name: The name of the glyph to check for ink.
    Returns:
        True if the font has at least one contour associated with it.
    """
    if 'glyf' in font:
        return ttf_glyph_has_ink(font, name)
    elif ('CFF ' in font) or ('CFF2' in font):
        return cff_glyph_has_ink(font, name)
    else:
        raise Exception("Could not find 'glyf', 'CFF ', or 'CFF2' table.")


def filenames_ending_in(suffix, root):
    '''
    Returns a list of the filenames of all files in a given directory subtree
    that have the given filename suffix. Example: List all ".json" files.
    '''
    filenames = []
    for f in os.listdir(root):
        fullpath = os.path.join(root, f)
        if f.endswith(suffix):
            filenames.append(fullpath)
        if os.path.isdir(fullpath):
            filenames.extend(filenames_ending_in(suffix, fullpath))
    return filenames


def add_check_overrides(checkids, profile_tag, overrides):
    '''
    Overridden checkids have a suffix identifying the specific
    profile that customize their behaviour.

    This helper function adds them to the list of checks and
    ensures the original check is not redundantly listed.
    '''

    # First we add the overridden check ids:
    checkids += [f'{checkid}:{profile_tag}'
                 for checkid in overrides]

    # But then we also remove the original check ids that
    # may have also been included from the original profile:
    checkids[:] = [checkid for checkid in checkids
                   if checkid not in overrides]
    return checkids


def can_shape(ttFont, text, parameters=None):
    '''
    Returns true if the font can render a text string without any
    .notdef characters.
    '''
    filename = ttFont.reader.file.name
    vharfbuzz = Vharfbuzz(filename)
    buf = vharfbuzz.shape(text, parameters)
    return all(g.codepoint != 0 for g in buf.glyph_infos)


def all_kerning(ttFont):
    if "GPOS" not in ttFont:
        return []
    rules = []

    def _invertClassDef(a, font):
        classes = {}
        for glyph, klass in a.items():
            if klass not in classes:
                classes[klass] = []
            classes[klass].append(glyph)
        glyphset = set(font.getGlyphOrder())
        classes[0] = glyphset - set(a.keys())
        return classes

    kern_subtables = []
    for lu in ttFont["GPOS"].table.LookupList.Lookup:
        for subtable in lu.SubTable:
            if subtable.LookupType == 9:
                subtable = subtable.ExtSubTable
            if subtable.LookupType == 2:
                kern_subtables.append(subtable)

    for subtable in kern_subtables:
        if subtable.Format == 1:
            for g, pair in zip(subtable.Coverage.glyphs, subtable.PairSet):
                for vr in pair.PairValueRecord:
                    rules.append((g, vr.SecondGlyph, vr.Value1, vr.Value2))
        else:
            class1 = _invertClassDef(subtable.ClassDef1.classDefs, ttFont)
            class2 = _invertClassDef(subtable.ClassDef2.classDefs, ttFont)
            for ix1, c1 in enumerate(subtable.Class1Record):
                if ix1 not in class1:
                    continue
                for ix2, c2 in enumerate(c1.Class2Record):
                    if ix2 not in class2:
                        continue
                    firstClass = list(
                        set(class1[ix1]) & set(subtable.Coverage.glyphs)
                    )
                    for left in firstClass:
                        for right in class2[ix2]:
                            rules.append((left, right, c2.Value1, c2.Value2))
    return rules
