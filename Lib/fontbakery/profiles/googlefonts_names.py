from fontbakery.profiles.googlefonts_axis_registry import AxisRegistry
from fontbakery.constants import (
    RIBBI_STYLE_NAMES,
    NameID,
    WindowsLanguageID,
    PlatformID,
    UnicodeEncodingID,
)
from fontTools.ttLib import TTFont
import logging


__all__ = ["GFNames"]


log = logging.Logger(__name__)


class GFNameData:
    # TODO: Add more
    AXIS_ORDER = ["GRAD", "opsz", "wdth", "wght", "ital"]

    GF_WEIGHTS = {
        "Thin": 100,
        "ExtraLight": 200,
        "Light": 300,
        "Regular": 400,
        "Medium": 500,
        "SemiBold": 600,
        "Bold": 700,
        "ExtraBold": 800,
        "Black": 900,
        # Italics
        "Thin Italic": 100,
        "ExtraLight Italic": 200,
        "Light Italic": 300,
        "Italic": 400,
        "Medium Italic": 500,
        "SemiBold Italic": 600,
        "Bold Italic": 700,
        "ExtraBold Italic": 800,
        "Black Italic": 900,
    }

    def __init__(self, ttFont):
        """Infer font names and related properties from a TTFont instance.

        To establish the correct names, we need a single source of truth
        for both static and variable fonts. For static fonts, we use the
        application font menu names. For Variable fonts, we use the same
        menu names and a mapping which maps fvar axis values to fallback
        names in our Axis Registry.

        Note: A variable font's name table records must reflect the zero
        origin of the font. In many cases, the origin isn't simply
        "Regular", it could be "Condensed Thin" etc. To find the origin,
        we map the default axis values to the Google Fonts Axis Registry
        e.g:

        fvar_dflts = {"wght": 200, "wdth": 75, "ital": "Italic}
        Style name will be: "Condensed ExtraLight Italic"

        GF Axis Reg: https://github.com/google/fonts/tree/main/axisregistry
        """
        self.ttFont = ttFont
        self.filename = self.ttFont.reader.file.name
        self.nametable = self.ttFont["name"]
        self.axis_reg = AxisRegistry()
        self.unregistered_tokens = set()
        self.axis_tokens = {}

        self.existing_family_name = self._get_best_family_name()
        self.existing_style_name = self._get_best_style_name()
        self.existing_family_name_tokens = [
            t
            for t in self.existing_family_name.split()
            if t not in self.existing_style_name.split()
        ]
        self.existing_style_name_tokens = [
            t
            for t in self.existing_style_name.split()
            if t not in self.existing_family_name.split()
        ]

        if "fvar" in self.ttFont:
            self.build_vf_names()
        else:
            self.build_static_names()
        self.isRibbi = self.typoSubFamily is None

    def build_static_names(self):
        self._get_nametable_tokens()

        self.family = self._build_family_name()
        self.typoFamily = self._build_static_typo_family_name()
        self.subFamily = self._build_subfamily_name()
        self.typoSubFamily = self._build_static_typosubfamily_name()
        self.fullName = self._build_full_name()
        self.postscript = self._build_postscript_name()
        self.filename = self._build_static_filename()
        self.macFamily = self.typoFamily or self.family
        self.macSubFamily = self.typoSubFamily or self.subFamily
        self.fsSelection = None
        self.macStyle = None
        self.usWeightClass = self._build_weight_class()
        self.usWidthClass = None

    def build_vf_names(self):
        self._get_fvar_tokens()
        self._get_nametable_tokens()
        self._get_fvar_instance_tokens()

        self.family = self._build_family_name()
        self.typoFamily = self._build_vf_typo_family_name()
        self.subFamily = self._build_subfamily_name()
        self.typoSubFamily = self._build_vf_typosubfamily_name()
        self.postscript = self._build_postscript_name()
        self.fullName = self._build_full_name()
        self.filename = self._build_vf_filename()
        self.macFamily = self.typoFamily or self.family
        self.macSubFamily = self.typoSubFamily or self.subFamily
        self.fsSelection = None
        self.macStyle = None
        self.usWeightClass = self._build_weight_class()

    def _get_fvar_tokens(self):
        found = False
        for axis in self.ttFont["fvar"].axes:
            if axis.axisTag == "GRAD":
                if axis.defaultValue == 0:
                    # Skip it since it is a default value
                    continue
                found = True
                self.axis_tokens["GRAD"] = f"Grade{int(axis.defaultValue)}"
            elif axis.axisTag == "opsz":
                found = True
                self.axis_tokens["opsz"] = f"{int(axis.defaultValue)}pt"
            else:
                if axis.axisTag not in self.axis_reg:
                    if axis.axisTag not in self.unregistered_tokens:
                        log.warning(f'"{axis.axisTag}" is not in the GF Axis Registry')
                        self.unregistered_tokens.add(axis.axisTag)
                    continue
                for name, value in self.axis_reg[axis.axisTag]["fallbacks"].items():
                    if (
                        value == self.axis_reg[axis.axisTag]["message"].default_value
                        and name != "Regular"
                    ):
                        found = True
                        # Skip all fallbacks that have default_value apart from Regular
                        continue
                    if value == axis.defaultValue:
                        found = True
                        self.axis_tokens[axis.axisTag] = name
            if not found:
                self.unregistered_tokens.add(axis.axisTag)

    def _get_nametable_tokens(self):
        # Get tokens from style name
        for token in self.existing_style_name_tokens:
            axis_tag = self._fallback_name_to_axis_tag(token)
            if not axis_tag:
                log.warning(f'"{token}" is not a fallback in the GF Axis Registry')
                self.unregistered_tokens.add(token)
                continue
            if axis_tag in self.axis_tokens:
                continue
            self.axis_tokens[axis_tag] = token

    def _get_fvar_instance_tokens(self):
        instances = self.ttFont["fvar"].instances
        for inst in instances:
            name = self.nametable.getName(
                inst.subfamilyNameID,
                PlatformID.WINDOWS,
                UnicodeEncodingID.UNICODE_1_1,
                WindowsLanguageID.ENGLISH_USA,
            ).toUnicode()
            for token in name.split():
                axis_tag = self._fallback_name_to_axis_tag(token)
                if not axis_tag:
                    log.warning(f'"{token} is not a fallback in the GF Axis Registry')
                    self.unregistered_tokens.add(token)
                    continue
                if axis_tag in self.axis_tokens:
                    continue
                self.axis_tokens[axis_tag] = token

    def _get_best_family_name(self):
        family = self.nametable.getName(
            NameID.FONT_FAMILY_NAME,
            PlatformID.WINDOWS,
            UnicodeEncodingID.UNICODE_1_1,
            WindowsLanguageID.ENGLISH_USA,
        )
        typo_family = self.nametable.getName(
            NameID.TYPOGRAPHIC_FAMILY_NAME,
            PlatformID.WINDOWS,
            UnicodeEncodingID.UNICODE_1_1,
            WindowsLanguageID.ENGLISH_USA,
        )
        name = typo_family or family
        return name.toUnicode()

    def _get_best_style_name(self):
        sub_family = self.nametable.getName(
            NameID.FONT_SUBFAMILY_NAME,
            PlatformID.WINDOWS,
            UnicodeEncodingID.UNICODE_1_1,
            WindowsLanguageID.ENGLISH_USA,
        )
        typo_sub_family = self.nametable.getName(
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
            PlatformID.WINDOWS,
            UnicodeEncodingID.UNICODE_1_1,
            WindowsLanguageID.ENGLISH_USA,
        )
        name = typo_sub_family or sub_family
        return name.toUnicode()

    def _fallback_name_to_axis_tag(self, token):
        # TODO perhaps make this a method of GFAxisRegistry?
        for axis in self.axis_reg:
            for name, _ in self.axis_reg[axis]["fallbacks"].items():
                if name == token:
                    return axis
        return None

    def _build_family_name(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis not in self.axis_tokens:
                continue
            token_name = self.axis_tokens[axis]
            if token_name in RIBBI_STYLE_NAMES:
                continue
            tokens.append(token_name)
        return (
            " ".join(self.existing_family_name_tokens + tokens)
            .replace("Italic", "")
            .strip()
        )

    def _build_static_typo_family_name(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis not in self.axis_tokens:
                continue
            if axis not in ["wght", "ital"]:
                continue
            token = self.axis_tokens[axis]
            tokens.append(token)
        if all(t in RIBBI_STYLE_NAMES for t in tokens):
            return None
        # TODO more complex examples which include non registered axes
        return " ".join(t for t in self.existing_family_name_tokens)

    def _build_static_typosubfamily_name(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis not in self.axis_tokens:
                continue
            if axis not in ["wght", "ital"]:
                continue
            token = self.axis_tokens[axis]
            tokens.append(token)
        if all(t in RIBBI_STYLE_NAMES for t in tokens):
            return None
        return " ".join(tokens).replace("Regular Italic", "Italic").strip()

    def _build_vf_typo_family_name(self):
        for axis, token in self.axis_tokens.items():
            if token not in RIBBI_STYLE_NAMES:
                return " ".join(self.existing_family_name_tokens)
        return None

    def _build_vf_typosubfamily_name(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis in self.axis_tokens:
                tokens.append(self.axis_tokens[axis])
        name = " ".join(tokens).replace("Regular Italic", "Italic").strip()
        if name not in RIBBI_STYLE_NAMES:
            return name
        return None

    def _build_subfamily_name(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis in self.axis_tokens and axis in ["wght", "ital"]:
                tokens.append(self.axis_tokens[axis])
        if "Bold" in tokens and "Italic" in tokens:
            return "Bold Italic"
        elif "Italic" in tokens:
            return "Italic"
        elif "Bold" in tokens:
            return "Bold"
        return "Regular"

    def _build_vf_filename(self):
        fvar_axes = [a.axisTag for a in self.ttFont["fvar"].axes]
        name_axes = [v for k, v in self.axis_tokens.items() if k not in fvar_axes]
        name = self.existing_family_name
        if not name_axes:
            return f"{name}[{','.join(sorted(fvar_axes))}].ttf".replace(" ", "")
        return f"{name}-{''.join(sorted(name_axes))}[{','.join(sorted(fvar_axes))}].ttf".replace(
            " ", ""
        )

    def _build_static_filename(self):
        if self.typoFamily:
            return f"{self.typoFamily}-{self.typoSubFamily}.ttf".replace(" ", "")
        return f"{self.family}-{self.subFamily}.ttf".replace(" ", "")

    @property
    def menu_family_name(self):
        return self.typoFamily or self.family

    @property
    def menu_subFamily_name(self):
        return self.typoSubFamily or self.subFamily

    @property
    def isTTF(self):
        return self.filename.endswith(".ttf")

    def _build_full_name(self):
        return f"{self.menu_family_name} {self.menu_subFamily_name}"

    def _build_postscript_name(self):
        return f"{self.menu_family_name}-{self.menu_subFamily_name}".replace(" ", "")

    def _build_weight_class(self):
        found_value = None
        for name, weight_val in sorted(self.GF_WEIGHTS.items(), key=lambda k: len(k[0]), reverse=True):
            if name in self.menu_subFamily_name:
                found_value = weight_val
                break
        # override usWeightClass values for Thin and ExtraLight if font is an otf
        if not self.isTTF and found_value == 100:
            return 250
        if not self.isTTF and found_value == 200:
            return 275
        if not found_value:
            import pdb
            pdb.set_trace()
        return found_value

