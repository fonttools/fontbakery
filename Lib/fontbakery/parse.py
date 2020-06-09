"""Parse GF specific style properties for font styles or font instances."""
import re
from collections import namedtuple


__all__ = ["style_parse", "instance_parse"]


RIBBI_STYLES = ["Regular", "Italic", "Bold", "Bold Italic"] 

_WEIGHT_NAMES = {
    r"Th?i?n|wt100": "Thin",
    r"Ext?r?a?Li?g?h?t|wt200": "ExtraLight",
    r"Li?g?h?t|wt300": "Light",
    r"Re?gu?l?a?r?|wt400": "Regular",
    r"Me?di?u?m?|wt500":"Medium",
    r"Se?m?i?Bo?l?d|wt600": "SemiBold",
    r"Bo?l?d|wt700": "Bold",
    r"Ext?r?a?Bo?l?d|wt800": "ExtraBold",
    r"Bla?c?k|wt900": "Black",
    r"Ext?r?a?Bla?c?k|wt1000": "ExtraBlack"
}
_WIDTH_NAMES = {
    r"Ult?r?a?Co?n?d?e?n?s?e?d": "UltraCondensed",
    r"Ext?r?a?Co?n?d?e?n?s?e?d": "ExtraCondensed",
    r"Co?n?d?e?n?s?e?d": "Condensed",
    r"Se?m?i?Co?n?d?e?n?s?e?d": "SemiCondensed",
    r"Se?m?i?Exp?a?n?d?e?d": "SemiExpanded",
    r"Exp?a?n?d?e?d|Extended": "Expanded",
    r"Ext?r?a?Exp?a?n?d?e?d": "ExtraExpanded",
    r"Ult?r?a?Exp?a?n?d?e?d": "UltraExpanded",
}
_ITALIC_NAMES = {
    r"Ita?l?i?c?|Obli?q?u?e?": "Italic" 
}
_WEIGHT_VALUES = {
    "Thin": {"usWeightClass": 100, "fvar": 100.0},
    "ExtraLight": {"usWeightClass": 200, "fvar": 200.0},
    "Light": {"usWeightClass": 300, "fvar": 300.0},
    "Regular": {"usWeightClass": 400, "fvar": 400.0},
    "": {"usWeightClass": 400, "fvar": 400.0},
    "Medium": {"usWeightClass": 500, "fvar": 500.0},
    "SemiBold": {"usWeightClass": 600, "fvar": 600.0},
    "Bold": {"usWeightClass": 700, "fvar": 700.0},
    "ExtraBold": {"usWeightClass": 800, "fvar": 800.0},
    "Black": {"usWeightClass": 900, "fvar": 900.0},
    "ExtraBlack": {"usWeightClass": 1000, "fvar": 1000.0},
}
_WIDTH_VALUES = {
    "UltraCondensed": {"usWidthClass": 1, "fvar": 50.0},
    "ExtraCondensed": {"usWidthClass": 2, "fvar": 62.5},
    "Condensed": {"usWidthClass": 3, "fvar": 75.0},
    "SemiCondensed": {"usWidthClass": 4, "fvar": 87.5},
    "": {"usWidthClass": 5, "fvar": 100.0},
    "SemiExpanded": {"usWidthClass": 6, "fvar": 112.5},
    "Expanded": {"usWidthClass": 7, "fvar": 125.0},
    "ExtraExpanded": {"usWidthClass": 8, "fvar": 150.0},
    "UltraExpanded": {"usWidthClass": 9, "fvar": 200.0},
}

def _re_string_tokenizer(string, mapping):
    found = []
    for k, v in mapping.items():
        result = re.search(k, string)
        if result:
            found.append(v)
    if not found:
        return None
    return sorted(found, key=len, reverse=True)[0]


def _get_opsz_token(string):
    result = re.search(r"[0-9]{1,4}pt", string)
    if result:
        return result.group(0)
    return None


def _opsz_values(string):
    if not string:
        return 0.
    return float(string.replace("pt", ""))


def _style_tokens(string):
    string = re.sub(r"\W", "", string)
    opsz = _get_opsz_token(string) or ""
    wdth = _re_string_tokenizer(string, _WIDTH_NAMES) or ""
    wght = _re_string_tokenizer(string, _WEIGHT_NAMES) or ""
    ital = _re_string_tokenizer(string, _ITALIC_NAMES) or ""
    return opsz, wdth, wght, ital


def _parse_name(opsz, wdth, wght, ital):
    if wght == "Regular" and ital == "Italic":
        wght = ""
    result = "{} {} {} {}".format(opsz, wdth, wght, ital).lstrip().rstrip()
    # replace multiple whitespace characters with a single space"
    return re.sub(r"\W+", " ", result)


def _win_style_name(string):
    if "Italic" in string:
        if string in ["Italic", "Bold Italic"]:
            return string
        return "Italic"
    elif string not in ["Regular", "Bold"]:
        return "Regular"
    return string


def _typo_style_name(string):
    if string not in RIBBI_STYLES:
        return string
    return None


def _fsSelection(string):
    result = 0b0
    if string == "Bold":
        result |= 0b100000
    if "Italic" in string:
        result |= 0b1
    if result == 0b0:
        result |= 0b1000000
    return result


def _macStyle(string):
    result = 0b0
    if string == "Bold":
        result |= 0b1
    if "Italic" in string:
        result |= 0b10
    return result


def _style_parse(string):
    """Parse a string into a GF font style object. All parsed properties
    conform to the Google Fonts specification.
    """
    _GFStyle = namedtuple("GFStyle",
                          """name
                          usWeightClass
                          usWidthClass
                          win_style_name
                          mac_style_name
                          typo_style_name
                          fsSelection
                          macStyle
                          is_ribbi
                          filename""")
    opsz, wdth, wght, ital = _style_tokens(string)
    name = _parse_name(opsz, wdth, wght, ital)
    return _GFStyle(name=name,
                    usWeightClass=_WEIGHT_VALUES[wght]['usWeightClass'],
                    usWidthClass=_WIDTH_VALUES[wdth]["usWidthClass"],
                    win_style_name=_win_style_name(name),
                    mac_style_name=name,
                    typo_style_name=_typo_style_name(name),
                    fsSelection=_fsSelection(wght),
                    macStyle=_macStyle(wght),
                    is_ribbi=name in RIBBI_STYLES,
                    filename=name.replace(" ", ""))


def style_parse(ttFont):
    """Get style properites from a TTFont object. If the font is a static font,
    use the filename to get style info, else if the font is a variable font,
    use the default instance's subfamilyNameID record"""
    if 'fvar' in ttFont:
        dflt_instance_coords = {a.axisTag: a.defaultValue for a in ttFont['fvar'].axes}
        for instance in ttFont['fvar'].instances:
            if instance.coordinates == dflt_instance_coords:
                name = ttFont['name'].getName(instance.subfamilyNameID, 3, 1, 1033).toUnicode()
                return _style_parse(name)
    import os
    filename = os.path.basename(ttFont.reader.file.name)
    if len(filename.split("-")) != 2:
        style = "Regular"
    else:
        style = filename.split("-")[1].split(".")[0]
    return _style_parse(style)


def instance_parse(string):
    """Derive instance properties from a string."""
    _GFInstance = namedtuple("GFStyle",
                             """name
                             coordinates
                             unparsable_tokens
                             raw_token_order
                             expected_token_order""")
    opsz, wdth, wght, ital = _style_tokens(string)
    if not wght:
        wght = "Regular"
    name = _parse_name(opsz, wdth, wght, ital)
    coords = {}
    if opsz:
        coords['opsz'] = _opsz_values(opsz)
    if wdth:
        coords['wdth'] = _WIDTH_VALUES[wdth]['fvar']
    if wght:
        coords['wght'] = _WEIGHT_VALUES[wght]['fvar']
    return _GFInstance(
        name=name,
        coordinates=coords,
        unparsable_tokens=_unparsable_tokens(string),
        raw_token_order=_token_order(string),
        expected_token_order=_token_order(name))


def _unparsable_tokens(string):
    string = string.split()
    results = []
    for word in string:
        if not any(_style_tokens(word)):
            results.append(word)
    return results


def _token_order(string):
    tokens = string.split()
    results = []
    for token in tokens:
        width_token = _re_string_tokenizer(token, _WIDTH_NAMES)
        if _get_opsz_token(token):
            results.append('opsz')
        elif _re_string_tokenizer(token, _WEIGHT_NAMES):
            results.append('wght')
        elif width_token and _WIDTH_VALUES[width_token] != 100:
            results.append("wdth")
    return results

