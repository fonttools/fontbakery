from fontbakery.profiles.googlefonts_conditions import GFAxisRegistry
from fontTools.ttLib import TTFont
import logging


RIBBI = ("Regular", "Italic", "Bold", "Bold Italic")


log = logging.Logger(__name__)


class GFSpec:
    # TODO: Add more
    AXIS_ORDER = ["GRAD", "opsz", "wdth", "wght", "ital"]

    def __init__(self, ttFont):
        """Infer font properties from a font's Family Name,
        Style Name and the Google Fonts Axis Registry"""
        self.ttFont = ttFont
        self.nametable = self.ttFont["name"]
        self.axis_reg = GFAxisRegistry()
        self.unregistered_tokens = []
        self.axis_tokens = {}
        # Get tokens from name table records. If axis token already exists, skip.
        self.existing_family_name = self._get_family_name()
        self.existing_style_name = self._get_style_name()

        self.family_name_tokens = [
            t
            for t in self.existing_family_name.split()
            if t not in self.existing_style_name.split()
        ]
        self.style_name_tokens = [
            t
            for t in self.existing_style_name.split()
            if t not in self.existing_family_name.split()
        ]

        self._get_tokens()

        if "fvar" in self.ttFont:
            self.build_vf_names()
        else:
            self.build_static_names()

    def _get_tokens(self):
        tokens = {}
        if "fvar" in self.ttFont:
            self._get_fvar_tokens()

        self._get_name_tokens()

        if "fvar" in self.ttFont:
            self._get_instance_tokens()

    def _get_fvar_tokens(self):
        found = False
        for axis in self.ttFont["fvar"].axes:
            if axis.axisTag == "GRAD":
                if axis.defaultValue == 0:
                    found = True
                    continue
                found = True
                self.axis_tokens["GRAD"] = f"Grade{int(axis.defaultValue)}"
            elif axis.axisTag == "opsz":
                found = True
                self.axis_tokens["opsz"] = f"{int(axis.defaultValue)}pt"
            else:
                if axis.axisTag not in self.axis_reg:
                    log.warning(f'"{axis.axisTag}" is not in the GF Axis Registry')
                    self.unregistered_tokens.append(axis.axisTag)
                    continue
                for name, value in self.axis_reg[axis.axisTag]["fallbacks"].items():
                    if (
                        value == self.axis_reg[axis.axisTag]["message"].default_value
                        and name != "Regular"
                    ):
                        found = True
                        continue
                    if value == axis.defaultValue:
                        found = True
                        self.axis_tokens[axis.axisTag] = name
            if not found:
                self.unregistered_tokens.append(axis.axisTag)

    def _get_name_tokens(self):
        # Get tokens from style name
        for token in self.style_name_tokens:
            axis_tag = self._token_to_axis(token)
            if not axis_tag:
                log.warning(f'"{token} is not a fallback in the GF Axis Registry')
                self.unregistered_tokens.append(token)
                continue
            if axis_tag in self.axis_tokens:
                continue
            self.axis_tokens[axis_tag] = token

    def _get_instance_tokens(self):
        instances = self.ttFont["fvar"].instances
        for inst in instances:
            name = self.nametable.getName(inst.subfamilyNameID, 3, 1, 0x409).toUnicode()
            for token in name.split():
                axis_tag = self._token_to_axis(token)
                if not axis_tag:
                    log.warning(f'"{token} is not a fallback in the GF Axis Registry')
                    self.unregistered_tokens.append(token)
                    continue
                if axis_tag in self.axis_tokens:
                    continue
                self.axis_tokens[axis_tag] = token

    def _get_family_name(self):
        family = self.nametable.getName(1, 3, 1, 0x409)
        typo_family = self.nametable.getName(16, 3, 1, 0x409)
        name = typo_family or family
        return name.toUnicode()

    def _get_style_name(self):
        sub_family = self.nametable.getName(2, 3, 1, 0x409)
        typo_sub_family = self.nametable.getName(17, 3, 1, 0x409)
        name = typo_sub_family or sub_family
        return name.toUnicode()

    def _token_to_axis(self, token):
        # TODO perhaps make this a method of GFAxisRegistry?
        for axis in self.axis_reg:
            for name, _ in self.axis_reg[axis]["fallbacks"].items():
                if name == token:
                    return axis
        return None

    def build_static_names(self):
        self.family = self._build_family()
        self.typoFamily = self._build_static_typo_family()
        self.subFamily = self._build_subfamily()
        self.typoSubFamily = self._build_static_typosubfamily()
        self.filename = self._build_static_filename()

    def build_vf_names(self):
        self.family = self._build_family()
        self.typoFamily = self._build_vf_typo_family()
        self.subFamily = self._build_subfamily()
        self.typoSubFamily = self._build_vf_typosubfamily()
        self.filename = self._build_vf_filename()

    def _build_family(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis not in self.axis_tokens:
                continue
            token_name = self.axis_tokens[axis]
            if token_name in RIBBI:
                continue
            tokens.append(token_name)
        return " ".join(self.family_name_tokens + tokens).replace("Italic", "").strip()

    def _build_static_typo_family(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis not in self.axis_tokens:
                continue
            if axis not in ["wght", "ital"]:
                continue
            token = self.axis_tokens[axis]
            tokens.append(token)
        if all(t in RIBBI for t in tokens):
            return None

        # TODO more complex examples which include non registered axes
        return " ".join(t for t in self.family_name_tokens)

    def _build_static_typosubfamily(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis not in self.axis_tokens:
                continue
            if axis not in ["wght", "ital"]:
                continue
            token = self.axis_tokens[axis]
            tokens.append(token)
        if all(t in RIBBI for t in tokens):
            return None
        return " ".join(tokens).replace("Regular Italic", "Italic").strip()

    def _build_vf_typo_family(self):
        for axis, token in self.axis_tokens.items():
            if token not in RIBBI:
                return " ".join(self.family_name_tokens)
        return None

    def _build_vf_typosubfamily(self):
        tokens = []
        for axis in self.AXIS_ORDER:
            if axis in self.axis_tokens:
                tokens.append(self.axis_tokens[axis])
        name = " ".join(tokens).replace("Regular Italic", "Italic").strip()
        if name not in RIBBI:
            return name
        return None

    def _build_subfamily(self):
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
            return f"{name}[{','.join(fvar_axes)}].ttf".replace(" ", "")
        return f"{name}-{''.join(name_axes)}[{','.join(sorted(fvar_axes))}].ttf".replace(
            " ", ""
        )

    def _build_static_filename(self):
        if self.typoFamily:
            return f"{self.typoFamily}-{self.typoSubFamily}.ttf".replace(" ", "")
        return f"{self.family}-{self.subFamily}.ttf".replace(" ", "")
