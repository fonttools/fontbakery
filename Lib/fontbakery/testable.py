import os
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional, List

from fontTools.ttLib import TTFont


@dataclass
class Testable:
    file: str
    context: Optional["CheckRunContext"] = None
    singular = "testable"
    plural = "testables"

    @property
    def file_displayname(self):
        return os.path.basename(self.file)


@dataclass
class Readme(Testable):
    singular = "readme_md"
    plural = "readme_mds"
    extensions = ["README.md"]
    description = "Project's README markdown file"

    @cached_property
    def readme_contents(self):
        return open(self.file, "r", encoding="utf-8").read()

    @cached_property
    def readme_directory(self):
        return os.path.dirname(self.file) or "."


@dataclass
class Ufo(Testable):
    singular = "ufo"
    plural = "ufos"
    extensions = [".ufo"]
    description = "UFO source"


@dataclass
class Designspace(Testable):
    singular = "designspace"
    plural = "designspaces"
    extensions = [".designspace"]
    description = "designspace source"


@dataclass
class GlyphsFile(Testable):
    singular = "glyphs_file"
    plural = "glyphs_files"
    extensions = [".glyphs", ".glyphspackage"]
    description = "Glyphs source"


@dataclass
class MetadataPB(Testable):
    singular = "metadata_pb"
    plural = "metadata_pbs"
    extensions = ["METADATA.pb"]
    description = "Project's METADATA protobuf file"


@dataclass
class Font(Testable):
    plural = "fonts"
    singular = "font"
    description = "OpenType binary"
    extensions = ["otf", "ttf"]

    @cached_property
    def ttFont(self):
        return TTFont(self.file)

    @cached_property
    def style(self):
        """Determine font style from canonical filename."""
        from fontbakery.constants import STATIC_STYLE_NAMES

        acceptable_stylenames = [name.replace(" ", "") for name in STATIC_STYLE_NAMES]
        filename = os.path.basename(self.file)
        # VF
        if self.is_variable_font:
            if self.default_wght_coord == 700.0:
                if "Italic" in filename:
                    return "BoldItalic"
                else:
                    return "Bold"
            else:
                if "Italic" in filename:
                    return "Italic"
                else:
                    return "Regular"
        # Static
        elif "-" in filename:
            stylename = os.path.splitext(filename)[0].split("-")[1]
            if stylename in acceptable_stylenames:
                return stylename
        return None

    @cached_property
    def is_variable_font(self):
        return "fvar" in self.ttFont.keys()

    @cached_property
    def is_ttf(self):
        return "glyf" in self.ttFont

    @cached_property
    def is_cff(self):
        return "CFF " in self.ttFont

    @cached_property
    def is_cff2(self):
        return "CFF2" in self.ttFont

    @cached_property
    def has_name_table(self):
        return "name" in self.ttFont.keys()

    @cached_property
    def has_os2_table(self):
        return "OS/2" in self.ttFont.keys()

    @cached_property
    def has_STAT_table(self):
        return "STAT" in self.ttFont

    @cached_property
    def axes_by_tag(self):
        if self.is_variable_font:
            return {axis.axisTag: axis for axis in self.ttFont["fvar"].axes}
        return {}

    @cached_property
    def has_wght_axis(self):
        return "wght" in self.axes_by_tag

    @cached_property
    def has_slnt_axis(self):
        return "slnt" in self.axes_by_tag

    @cached_property
    def has_ital_axis(self):
        return "ital" in self.axes_by_tag

    @cached_property
    def has_opsz_axis(self):
        return "opsz" in self.axes_by_tag

    @cached_property
    def has_wdth_axis(self):
        return "wdth" in self.axes_by_tag

    @cached_property
    def family_directory(self):
        """Get the path of font project directory."""
        return os.path.dirname(self.file) or "."

    @cached_property
    def is_hinted(self):
        return "fpgm" in self.ttFont

    @cached_property
    def slnt_axis(self):
        return self.axes_by_tag.get("slnt")

    @cached_property
    def opsz_axis(self):
        return self.axes_by_tag.get("opsz")

    @cached_property
    def ital_axis(self):
        return self.axes_by_tag.get("ital")

    @cached_property
    def grad_axis(self):
        return self.axes_by_tag.get("GRAD")

    @cached_property
    def wght_axis(self):
        return self.axes_by_tag.get("wght")

    @cached_property
    def default_wght_coord(self):
        if self.wght_axis:
            return self.wght_axis.defaultValue

    @cached_property
    def font_codepoints(self):
        return set(self.ttFont.getBestCmap().keys())

    @cached_property
    def preferred_cmap(self):
        from fontbakery.utils import get_preferred_cmap

        return get_preferred_cmap(self.ttFont)

    @cached_property
    def is_italic(self):
        from fontbakery.constants import FsSelection, MacStyle
        from fontbakery.utils import keyword_in_full_font_name

        ttFont = self.ttFont
        return (
            ("OS/2" in ttFont and ttFont["OS/2"].fsSelection & FsSelection.ITALIC)
            or ("head" in ttFont and ttFont["head"].macStyle & MacStyle.ITALIC)
            or keyword_in_full_font_name(ttFont, "italic")
            or ("post" in ttFont and ttFont["post"].italicAngle)
        )

    @cached_property
    def is_bold(self):
        from fontbakery.constants import FsSelection, MacStyle
        from fontbakery.utils import (
            keyword_in_full_font_name,
            bold_adjacent_styles_in_full_font_name,
        )

        ttFont = self.ttFont
        return (
            ("OS/2" in ttFont and ttFont["OS/2"].fsSelection & FsSelection.BOLD)
            or ("head" in ttFont and ttFont["head"].macStyle & MacStyle.BOLD)
            or (
                keyword_in_full_font_name(ttFont, "bold")
                and not bold_adjacent_styles_in_full_font_name(ttFont)
            )
        )


@dataclass
class TTCFont(Font):
    index: int = 0

    @cached_property
    def ttFont(self):
        from fontTools.ttLib import TTCollection

        with open(self.file, "rb") as ttcfile:
            ttc = TTCollection(ttcfile)
            return ttc.fonts[self.index]

    @property
    def file_displayname(self):
        return os.path.basename(self.file) + "#" + str(self.index)


FILE_TYPES = [Readme, Ufo, Designspace, GlyphsFile, MetadataPB, Font]


@dataclass
class CheckRunContext:
    testables: List[Testable] = field(default_factory=list)
    config: dict = field(default_factory=dict)

    @cached_property
    def testables_by_type(self):
        by_type = defaultdict(list)
        for testable in self.testables:
            by_type[testable.singular].append(testable)
        return by_type

    @property  # Can't cache a map
    def ttFonts(self):
        return map(
            lambda font: font.ttFont, self.fonts  # pytype: disable=attribute-error
        )

    @cached_property
    def RIBBI_ttFonts(self):
        from fontbakery.constants import RIBBI_STYLE_NAMES

        # pytype: disable=attribute-error
        return [font.ttFont for font in self.fonts if font.style in RIBBI_STYLE_NAMES]
        # pytype: enable=attribute-error

    @cached_property
    def VFs(self):
        """Returns a list of font files which are recognized as variable fonts"""
        # pytype: disable=attribute-error
        return [font.ttFont for font in self.fonts if font.is_variable_font]
        # pytype: enable=attribute-error


for cls in FILE_TYPES:
    # context.fonts -> context.testables_by_type["font"]
    setattr(
        CheckRunContext,
        cls.plural,
        property(lambda self, cls=cls: self.testables_by_type[cls.singular]),
    )
