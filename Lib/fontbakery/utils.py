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
import subprocess
import sys
from typing import Text, Optional

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
import rich

from fontbakery.constants import NO_COLORS_THEME, DARK_THEME, LIGHT_THEME


def exit_with_install_instructions(profile_name):
    sys.exit(
        f"\nTo run the {profile_name} profile, one needs to install\n"
        f"fontbakery with the '{profile_name}' extra, like this:\n\n"
        f"    python -m pip install -U 'fontbakery[{profile_name}]'\n\n"
    )


def remove_white_space(s):
    s = s.replace(" ", "")
    s = s.replace("\t", "")
    s = s.replace("\n", "")
    return s


# TODO: this should be part of FontBakeryCheck and check.conditions
# should be a tuple (negated, name)
def is_negated(name):
    stripped = name.strip()
    if stripped.startswith("not "):
        return True, stripped[4:].strip()
    return False, stripped


def get_apple_terminal_bg_color():
    """Runs an AppleScript snippet that returns the RGB values of the
    background color of the active Apple Terminal window."""
    line_1 = 'tell application "Terminal"'
    line_2 = "    get background color of selected tab of window 1"
    line_3 = "end tell"
    output = subprocess.run(
        ["osascript", "-e", line_1, "-e", line_2, "-e", line_3],
        text=True,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    return output.strip()


def apple_terminal_bg_is_white():
    """Returns a boolean indicating if the background color
    of Apple's Terminal is white."""
    is_apple_terminal = os.getenv("TERM_PROGRAM") == "Apple_Terminal"
    if is_apple_terminal:
        bg_color = get_apple_terminal_bg_color()
        if bg_color == "65535, 65535, 65535":
            return True
    return False


def get_theme(args):
    if args.no_colors:
        return NO_COLORS_THEME
    if args.light_theme:
        return LIGHT_THEME
    if args.dark_theme:
        return DARK_THEME
    if sys.platform == "darwin":
        # Apple's Terminal default profile is called 'Basic' and has a white background.
        # But the user may have switched to a different profile, or even to a different
        # terminal app. Default to the light-theme only if we're sure that the terminal
        # app is Apple's Terminal and its background color is indeed white.
        return LIGHT_THEME if apple_terminal_bg_is_white() else DARK_THEME
    # For orther systems like GNU+Linux and Windows, a dark terminal may be more common.
    return DARK_THEME


def unindent_and_unwrap_rationale(rationale, checkid=None):
    """Takes the 'rationale' docstring of a check and removes indents and hard line
    breaks that were added to long lines."""
    content = ""

    for line in rationale.split("\n"):
        soft_return = line.endswith("⏎")  # U+23CE
        stripped_line = line.strip()
        new_paragraph = len(stripped_line) == 0

        if new_paragraph:
            content = content.rstrip()
            content += "\n\n"

        else:
            content += stripped_line

            if soft_return:
                content = f"{content[:-1]}\n"
            else:
                content += " "

    return f"\n{content.strip()}\n"


def split_camel_case(camelcase):
    chars = []
    for i, char in enumerate(camelcase):
        if char.isupper() and i > 0:
            chars.append(" ")
        chars.append(char)

    return "".join(chars)


def pretty_print_list(config, values, shorten=10, sep=", ", glue=" and "):
    if len(values) == 1:
        return str(values[0])

    if config.get("full_lists"):
        shorten = None

    if shorten and len(values) > shorten + 2:
        joined_items_str = sep.join(map(str, values[:shorten]))
        return (
            f"{joined_items_str}{glue}{len(values) - shorten} more.\n"
            f"\n"
            f"Use -F or --full-lists to disable shortening of long lists."
        )
    else:
        joined_items_str = sep.join(map(str, values[:-1]))
        return f"{joined_items_str}{glue}{str(values[-1])}"


def bullet_list(config, items, bullet="-", indentation="\t"):
    return f"{indentation}{bullet} " + pretty_print_list(
        config,
        items,
        sep=f"\n\n{indentation}{bullet} ",
        glue=f"\n\n{indentation}{bullet} ",
    )


def markdown_table(items):
    """Format a list of dicts into a markdown table.

    >>> markdown_table(
    >>>    [{"name": "Sam", "age": 30}, {"name": "Ash", "age": 25}]
    >>> )
    ...
    | name | age  |
    | :--- | :--- |
    | Sam  | 30   |
    | Ash  | 25   |
    """
    res = []
    header = "| " + " | ".join(items[0].keys()) + " |"
    res.append(header)
    lb = "|" + " :--- |" * len(items[0])
    res.append(lb)
    for row in items:
        vals = list(row.values())
        r = "| " + " | ".join(map(str, vals)) + " |"
        res.append(r)
    return "\n".join(res)


def get_regular(fonts):
    # TODO: Maybe also support getting a regular instance from a variable font?
    for font in fonts:
        if "-Regular.ttf" in font.file:
            return font


def filesize_formatting(s):
    if s < 1024:
        return f"{s} bytes"
    elif s < 1024 * 1024:
        return f"{s/1024:.1f}kb"
    else:
        return f"{s/(1024*1024):.1f}Mb"


def get_bounding_box(font):
    """Returns max and min bbox of given truetype font"""
    ymin = 0
    ymax = 0
    if font.sfntVersion == "OTTO":
        ymin = font["head"].yMin
        ymax = font["head"].yMax
    else:
        for g in font["glyf"].glyphs:
            char = font["glyf"][g]
            if hasattr(char, "yMin") and ymin > char.yMin:
                ymin = char.yMin
            if hasattr(char, "yMax") and ymax < char.yMax:
                ymax = char.yMax
    return ymin, ymax


def get_name_entries(font, nameID, platformID=None, encodingID=None, langID=None):
    results = []
    for entry in font["name"].names:
        if (
            entry.nameID == nameID
            and (platformID is None or entry.platformID == platformID)
            and (encodingID is None or entry.platEncID == encodingID)
            and (langID is None or entry.langID == langID)
        ):
            results.append(entry)
    return results


def get_name_entry_strings(font, nameID, platformID=None, encodingID=None, langID=None):
    entries = get_name_entries(font, nameID, platformID, encodingID, langID)
    return list(map(lambda e: e.string.decode(e.getEncoding()), entries))


def name_entry_id(name):
    from fontbakery.constants import NameID, PlatformID

    return "[{}({}):{}({})]".format(
        NameID(name.nameID).name,
        name.nameID,
        PlatformID(name.platformID).name,
        name.platformID,
    )  # pylint: disable=consider-using-f-string


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
    items = [font["glyf"][name]]

    while items:
        g = items.pop(0)
        if g.isComposite():
            for comp in g.components:
                if comp.glyphName != ".ttfautohint":
                    items.append(font["glyf"][comp.glyphName])
        if g.numberOfContours != -1:
            contour_count += g.numberOfContours
    return contour_count


def get_font_glyph_data(font):
    """Return information for each glyph in a font"""
    from fontbakery.constants import PlatformID, WindowsEncodingID

    font_data = []

    try:
        subtable = font["cmap"].getcmap(
            PlatformID.WINDOWS, WindowsEncodingID.UNICODE_BMP
        )
        if not subtable:
            # Well... Give it a chance here...
            # It may be using a different Encoding_ID value
            subtable = font["cmap"].tables[0]

        cmap = subtable.cmap
    except (AttributeError, IndexError, KeyError):
        return None

    cmap_reversed = dict(zip(cmap.values(), cmap.keys()))

    for glyph_name in font.getGlyphSet().keys():
        if glyph_name in cmap_reversed:
            uni_glyph = cmap_reversed[glyph_name]
            contours = glyph_contour_count(font, glyph_name)
            font_data.append(
                {"unicode": uni_glyph, "name": glyph_name, "contours": {contours}}
            )
    return font_data


def get_Protobuf_Message(klass, path):
    try:
        from google.protobuf import text_format
    except ImportError:
        exit_with_install_instructions("googlefonts")

    message = klass()
    text_data = open(path, "rb").read()
    text_format.Merge(text_data, message)
    return message


def get_FamilyProto_Message(path):
    try:
        from fontbakery.fonts_public_pb2 import FamilyProto
    except ImportError:
        exit_with_install_instructions("googlefonts")

    return get_Protobuf_Message(FamilyProto, path)


def get_DesignerInfoProto_Message(text_data):
    try:
        from fontbakery.designers_pb2 import DesignerInfoProto
        from google.protobuf import text_format
    except ImportError:
        exit_with_install_instructions("googlefonts")

    message = DesignerInfoProto()
    text_format.Merge(text_data, message)
    return message


def check_bit_entry(ttFont, table, attr, expected, bitmask, bitname):
    from fontbakery.message import Message
    from fontbakery.status import PASS, FAIL

    value = getattr(ttFont[table], attr)
    name_str = f"{table} {attr} {bitname} bit"
    if bool(value & bitmask) == expected:
        return PASS, f"{name_str} is properly set."
    else:
        if expected:
            expected_str = "set"
        else:
            expected_str = "unset"
        return FAIL, Message(f"bad-{bitname}", f"{name_str} should be {expected_str}.")


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
                " to install the certificates."
            )


def cff_glyph_has_ink(font: TTFont, glyph_name: Text) -> bool:
    if "CFF2" in font:
        top_dict = font["CFF2"].cff.topDictIndex[0]
    else:
        top_dict = font["CFF "].cff.topDictIndex[0]
    char_strings = top_dict.CharStrings
    char_string = char_strings[glyph_name]
    bounds = char_string.calcBounds(char_strings)
    if bounds is not None:
        return True

    return False


def ttf_glyph_has_ink(font: TTFont, name: Text) -> bool:
    glyph = font["glyf"].glyphs[name]
    glyph.expand(font["glyf"])

    if not glyph.isComposite():
        if glyph.numberOfContours == 0:
            return False
        (coords, _, _) = glyph.getCoordinates(font["glyf"])
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
                    result |= 1 << bit
    return result


def glyph_has_ink(font: TTFont, glyph_name: Text) -> bool:
    """Checks if specified glyph has any ink.

    That is, that it has at least one defined contour associated.
    Composites are considered to have ink if any of their components have ink.
    Args:
        font:       the font
        glyph_name: The name of the glyph to check for ink.
    Returns:
        True if the font has at least one contour associated with it.
    """
    if "glyf" in font:
        return ttf_glyph_has_ink(font, glyph_name)
    elif ("CFF " in font) or ("CFF2" in font):
        return cff_glyph_has_ink(font, glyph_name)
    else:
        raise Exception("Could not find 'glyf', 'CFF ', or 'CFF2' table.")


def filenames_ending_in(suffix, root):
    """
    Returns a list of the filenames of all files in a given directory subtree
    that have the given filename suffix. Example: List all ".json" files.
    """
    filenames = []
    for f in os.listdir(root):
        fullpath = os.path.join(root, f)
        if f.endswith(suffix):
            filenames.append(fullpath)
        if os.path.isdir(fullpath):
            filenames.extend(filenames_ending_in(suffix, fullpath))
    return filenames


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
                    firstClass = list(set(class1[ix1]) & set(subtable.Coverage.glyphs))
                    for left in firstClass:
                        for right in class2[ix2]:
                            rules.append((left, right, c2.Value1, c2.Value2))
    return rules


def iterate_lookup_list_with_extensions(ttFont, table, callback, *args):
    """Iterates over the lookup list of a font's GSUB/GPOS table, calling
    the callback with the lookup and the provided arguments, but descending
    into Extension subtables."""
    if table not in ttFont or not ttFont[table].table.LookupList:
        return

    extension_type = 9 if table == "GPOS" else 7

    for lookup in ttFont[table].table.LookupList.Lookup:
        if lookup.LookupType == extension_type:
            for xt in lookup.SubTable:
                original_LookupType = xt.LookupType
                try:
                    xt.SubTable = [xt.ExtSubTable]
                    xt.LookupType = xt.ExtSubTable.LookupType
                    callback(xt, *args)
                finally:
                    del xt.SubTable
                    xt.LookupType = original_LookupType
        else:
            callback(lookup, *args)


def axis(ttFont, tag):
    """Return the axis with the given tag."""
    for axis in ttFont["fvar"].axes:
        if axis.axisTag == tag:
            return axis


class PointsPen(BasePen):
    def __init__(self):
        super().__init__()
        self.points = []

    def _moveTo(self, pt):
        self.points.append(pt)

    def _lineTo(self, pt):
        self.points.append(pt)

    def _curveToOne(self, pt1, pt2, pt3):
        self.points.append(pt1)
        self.points.append(pt2)
        self.points.append(pt3)

    def _qCurveToOne(self, pt1, pt2):
        self.points.append(pt1)
        self.points.append(pt2)

    def _closePath(self):
        pass

    def _endPath(self):
        self.points = []
        self.beginPath()

    def getPoints(self):
        return self.points

    def highestPoint(self):
        highest = None
        for p in self.points:
            if highest is None or p[1] > highest[1]:  # pylint: disable=E1136
                highest = p
        return highest

    def lowestPoint(self):
        lowest = None
        for p in self.points:
            if lowest is None or p[1] < lowest[1]:  # pylint: disable=E1136
                lowest = p
        return lowest

    def _addComponent(self, glyphName, transformation):
        self.glyphSet[glyphName].draw(self)


class IndentedParagraph:
    def __init__(self, renderable, left=4, right=0, first=None):
        self.renderable = renderable
        self.left = left
        self.right = right
        if first is not None:
            self.first = first
        else:
            self.first = self.left

    def __rich_console__(self, console, options):
        style = console.get_style("none")
        width = options.max_width
        render_options = options.update_width(width - self.left - self.right)
        lines = console.render_lines(
            self.renderable, render_options, style=style, pad=True
        )
        _Segment = rich.segment.Segment

        left = _Segment(" " * self.left, style) if self.left else None
        first = _Segment(" " * self.first, style) if self.left else None
        right = (
            [_Segment(f'{" " * self.right}', style), _Segment.line()]
            if self.right
            else [_Segment.line()]
        )
        for ix, line in enumerate(lines):
            if ix == 0:
                yield first
            else:
                yield left
            yield from line
            yield from right


def keyword_in_full_font_name(ttFont, keyword):
    from fontbakery.constants import NameID

    for entry in ttFont["name"].names:
        if (
            entry.nameID == NameID.FULL_FONT_NAME
            and keyword in entry.string.decode(entry.getEncoding()).lower().split()
        ):
            return True
    return False


def bold_adjacent_styles_in_full_font_name(ttFont):
    from fontbakery.constants import NameID

    for entry in ttFont["name"].names:
        if entry.nameID == NameID.FULL_FONT_NAME and any(
            x in entry.string.decode(entry.getEncoding()).lower()
            for x in [
                "extra bold",
                "extrabold",
                "semi bold",
                "semibold",
                "demi bold",
                "demibold",
            ]
        ):
            return True
    return False


def show_inconsistencies(dictionary, config):
    """Display an 'inconsistencies dictionary' as a bullet list. Turns:

        { "value1": ["file1", "file2"], "value2": ["file3"] }

    into

        - value1: file1 and file2
        - value2: file3

    """
    return bullet_list(
        config,
        [
            f"{value}: {pretty_print_list(config, files)}"
            for value, files in dictionary.items()
        ],
    )


def image_dimensions(filename):
    if filename.lower().endswith(".png"):
        data = open(filename, "rb").read(24)
        if data[0:4] != b"\x89PNG" and data[12:16] != b"IHDR":
            return None  # Does not look like a PNG!

        w = data[16]
        w = w << 8 | data[17]
        w = w << 8 | data[18]
        w = w << 8 | data[19]

        h = data[20]
        h = h << 8 | data[21]
        h = h << 8 | data[22]
        h = h << 8 | data[23]
        return w, h

    elif filename.lower().endswith(".gif"):
        data = open(filename, "rb").read(10)
        if data[0:4] != b"GIF8":
            return None  # Does not look like a GIF!

        w = data[7]
        w = w << 8 | data[6]

        h = data[9]
        h = h << 8 | data[8]
        return w + 1, h + 1

    else:
        return None  # some other file format
