import os
import re
import yaml

from fontTools.ttLib.ttFont import TTFont

from fontbakery.callable import condition
from fontbakery.testable import Font, CheckRunContext
from fontbakery.constants import (
    NameID,
    PlatformID,
    UnicodeEncodingID,
    WindowsLanguageID,
)
from fontbakery.utils import exit_with_install_instructions
from fontbakery.checks.vendorspecific.googlefonts.utils import parse_html

# @condition
# def glyphsFile(glyphs_file):
#     import glyphsLib

#     return glyphsLib.load(open(glyphs_file, encoding="utf-8"))


@condition(Font)
def style_with_spaces(font):
    """Stylename with spaces (derived from a canonical filename)."""
    if font.style:
        return font.style.replace("Italic", " Italic").strip()


@condition(Font)
def expected_os2_weight(font):
    """The weight name and the expected OS/2 usWeightClass value inferred from
    the style part of the font name

    The Google Font's API which serves the fonts can only serve
    the following weights values with the corresponding subfamily styles:

    250, Thin
    275, ExtraLight
    300, Light
    400, Regular
    500, Medium
    600, SemiBold
    700, Bold
    800, ExtraBold
    900, Black

    Thin is not set to 100 because of legacy Windows GDI issues:
    https://www.adobe.com/devnet/opentype/afdko/topic_font_wt_win.html
    """
    if not font.style:
        return None
    style = font.style
    # Weight name to value mapping:
    GF_API_WEIGHTS = {
        "Thin": 250,
        "ExtraLight": 275,
        "Light": 300,
        "Regular": 400,
        "Medium": 500,
        "SemiBold": 600,
        "Bold": 700,
        "ExtraBold": 800,
        "Black": 900,
    }
    if style == "Italic":
        weight_name = "Regular"
    elif style.endswith("Italic"):
        weight_name = style.replace("Italic", "")
    else:
        weight_name = style

    expected = GF_API_WEIGHTS[weight_name]
    return weight_name, expected


@condition(CheckRunContext)
def stylenames_are_canonical(collection):
    """Are all font files named canonically ?"""
    return all(font.canonical_stylename for font in collection.fonts)


@condition(Font)
def canonical_stylename(font):
    """Returns the canonical stylename of a given font."""
    from fontbakery.constants import STATIC_STYLE_NAMES, VARFONT_SUFFIXES

    # remove spaces in style names
    valid_style_suffixes = [name.replace(" ", "") for name in STATIC_STYLE_NAMES]

    filename = os.path.basename(font.file)
    basename = os.path.splitext(filename)[0]
    s = "-".join(basename.split("-")[1:])
    varfont = os.path.exists(font.file) and font.is_variable_font
    if (
        "-" in basename
        and (s in VARFONT_SUFFIXES and varfont)
        or (s in valid_style_suffixes and not varfont)
    ):
        return s


@condition(Font)
def article(font):
    """Read article/ARTICLE.en_us.html file from a font directory."""
    descfile = os.path.join(os.path.dirname(font.file), "article", "ARTICLE.en_us.html")
    if os.path.exists(descfile):
        return open(descfile, "r", encoding="utf-8").read()
    else:
        return None


@condition(Font)
def article_html(font):
    return parse_html(font.article)


@condition(Font)
def descfile(font):
    """Get the path of the DESCRIPTION file of a given font project."""
    if font:
        directory = os.path.dirname(font.file)
        descfilepath = os.path.join(directory, "DESCRIPTION.en_us.html")
        if os.path.exists(descfilepath):
            return descfilepath


@condition(Font)
def description(font):
    """Get the contents of the DESCRIPTION file of a font project."""
    if not font.descfile:
        return
    import io

    return io.open(font.descfile, "r", encoding="utf-8").read()


@condition(Font)
def description_html(font):
    return parse_html(font.description)


@condition(Font)
def description_and_article(font):
    description = font.description
    article = font.article
    result = {}
    if description:
        result["description"] = description
    if article:
        result["article"] = article
    return result


@condition(Font)
def description_and_article_html(font):
    description = font.description_html
    article = font.article_html
    result = {}
    if description:
        result["description"] = description
    if article:
        result["article"] = article
    return result


@condition(Font)
def metadata_file(font, metadata_pb=None):
    if metadata_pb:
        if isinstance(metadata_pb, list):
            metadata_pb = metadata_pb[0]  # quirk

        return metadata_pb

    elif font.family_directory:
        pb_file = os.path.join(font.family_directory, "METADATA.pb")
        if os.path.exists(pb_file):
            return pb_file


@condition(Font)
def family_metadata_text_content(font):
    if not font.metadata_file:
        return

    return open(font.metadata_file, "r", encoding="utf-8").read()


@condition(Font)
def family_metadata(font):
    if not font.metadata_file:
        return

    try:
        from google.protobuf import text_format
    except ImportError:
        exit_with_install_instructions("googlefonts")

    from fontbakery.checks.vendorspecific.googlefonts.utils import (
        get_FamilyProto_Message,
    )

    try:
        return get_FamilyProto_Message(font.metadata_file)
    except text_format.ParseError:
        return None


@condition(Font)
def is_ofl(font):
    return font.license_filename and "OFL" in font.license_filename


@condition(Font)
def familyname(font):
    filename = os.path.basename(font.file)
    filename_base = os.path.splitext(filename)[0]
    if "-" in filename_base:
        return filename_base.split("-")[0]
    # Handle VFs e.g Inconsolata[wdth,wght] --> Inconsolata
    elif "[" in filename_base:
        return filename_base.split("[")[0]
    else:
        return filename_base


@condition(Font)
def google_familyname(font):
    # Google Fonts may not use the font's nameID 1 or 16 as the family name.
    # Instead, GF uses the metadata.display_name and if this isn't
    # available, it'll use the metadata.name. If neither of these are
    # available, it means the font isn't hosted on Google Fonts yet so
    # we'll use the font's best familyname.
    if not font.family_metadata:
        return font.best_familyname
    return (
        font.family_metadata.display_name
        or font.family_metadata.name
        or font.best_familyname
    )


@condition(Font)
def best_familyname(font):
    return font.ttFont["name"].getBestFamilyName()


@condition(Font)
def listed_on_gfonts_api(font):
    if not font.context.network or not font.google_familyname:
        return
    for item in font.context.production_metadata["familyMetadataList"]:
        if item["family"] == font.google_familyname:
            return True
    return False


@condition(Font)
def has_regular_style(font):
    fonts = font.family_metadata.fonts if font.family_metadata else []
    for f in fonts:
        if f.weight == 400 and f.style == "normal":
            return True
    return False


@condition(Font)
def font_metadata(font):
    if not font.family_metadata:
        return

    for f in font.family_metadata.fonts:
        if font.file.endswith(f.filename):
            return f


@condition(Font)
def font_familynames(font):
    from fontbakery.utils import get_name_entry_strings

    return get_name_entry_strings(font.ttFont, NameID.FONT_FAMILY_NAME)


@condition(Font)
def typographic_familynames(font):
    from fontbakery.utils import get_name_entry_strings

    return get_name_entry_strings(font.ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)


@condition(Font)
def font_familyname(font):
    # This assumes that all familyname
    # name table entries are identical.
    # FIX-ME: Maybe we should have a check for that.
    #         Have we ever seen this kind of
    #         problem in the wild, though ?
    return font.font_familynames[0]


@condition(Font)
def rfn_exception(font):
    """These are the very few font families where we accept usage of
    a Reserved Font Name. These are typically fonts that had already
    been published previously with an RFN, or fonts which benefit from
    an agreement with Google Fonts.
    """
    from pkg_resources import resource_filename

    rfn_exceptions_txt = "data/googlefonts/reserved_font_name_exceptions.txt"
    filename = resource_filename("fontbakery", rfn_exceptions_txt)
    for exception in open(filename, "r", encoding="utf-8").readlines():
        exception = exception.split("#")[0].strip()
        exception = exception.replace(" ", "")
        if exception == "":
            continue

        if exception in font.familyname:
            return True


@condition(Font)
def remote_styles(font):
    """Get a dictionary of TTFont objects of all font files of
    a given family as currently hosted at Google Fonts.
    """
    from fontbakery.utils import download_file
    import json
    import requests

    if not font.context.network or not font.listed_on_gfonts_api:
        return None

    # download_family_from_Google_Fonts
    dl_url = "https://fonts.google.com/download/list?family={}"
    family_name = font.google_familyname
    url = dl_url.format(family_name.replace(" ", "%20"))
    data = json.loads(requests.get(url, timeout=10).text[5:])
    remote_fonts = []
    for item in data["manifest"]["fileRefs"]:
        filename = item["filename"]
        dl_url = item["url"]
        if "static" in filename:
            continue
        if not filename.endswith(("otf", "ttf")):
            continue
        file_obj = download_file(dl_url)
        if file_obj:
            remote_fonts.append(TTFont(file_obj))

    rstyles = {}
    for remote_font in remote_fonts:
        if "fvar" in remote_font:
            for instance in remote_font["fvar"].instances:
                inst_subfamily = (
                    remote_font["name"]
                    .getName(instance.subfamilyNameID, 3, 1, 0x409)
                    .toUnicode()
                )
                rstyles[inst_subfamily] = remote_font
        else:
            rstyles[remote_font["name"].getBestSubFamilyName()] = remote_font
    return rstyles


@condition(Font)
def remote_style(font):
    font_style = font.ttFont["name"].getBestSubFamilyName()
    remote_styles = font.remote_styles
    if not remote_styles:
        return None
    return remote_styles.get(font_style)


@condition(Font)
def regular_remote_style(font):
    from fontbakery.checks.conditions import get_instance_axis_value

    remote_styles = font.remote_styles

    if not remote_styles:
        return None
    if "Regular" in remote_styles:
        return remote_styles["Regular"]

    for style_name, remote_font in remote_styles.items():
        if "fvar" in remote_font:
            if get_instance_axis_value(remote_font, "Regular", "wght"):
                return remote_font
    return list(remote_styles.items())[0][1]


@condition(CheckRunContext)
def regular_ttFont(context):
    from fontbakery.checks.conditions import get_instance_axis_value

    for ttFont in context.ttFonts:
        if "-Regular." in os.path.basename(ttFont.reader.file.name):
            return ttFont
        nametable = ttFont["name"]
        sub_family = nametable.getName(
            NameID.FONT_SUBFAMILY_NAME,
            PlatformID.WINDOWS,
            UnicodeEncodingID.UNICODE_1_1,
            WindowsLanguageID.ENGLISH_USA,
        )
        typo_sub_family = nametable.getName(
            NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
            PlatformID.WINDOWS,
            UnicodeEncodingID.UNICODE_1_1,
            WindowsLanguageID.ENGLISH_USA,
        )
        if sub_family and sub_family.toUnicode() == "Regular" and not typo_sub_family:
            return ttFont
        if "fvar" in ttFont:
            if get_instance_axis_value(ttFont, "Regular", "wght"):
                return ttFont
    return None


@condition(Font)
def familyname_with_spaces(self):
    """Attempts to build family name from font name.
    For example, HPSimplifiedSans => HP Simplified Sans.
    Args:
      familyname: The name of a font.
    Returns:
      The name of the family that should be in this font.
    """
    familyname = self.familyname
    # SomethingUpper => Something Upper
    familyname = re.sub("(.)([A-Z][a-z]+)", r"\1 \2", familyname)
    # Font3 => Font 3
    familyname = re.sub("([a-z])([0-9]+)", r"\1 \2", familyname)
    # lookHere => look Here
    familyname = re.sub("([a-z0-9])([A-Z])", r"\1 \2", familyname)

    def of_special_case(s):
        """Special case for family names such as
        MountainsofChristmas which would need to
        have the "of" split apart from "Mountains".

        See also: https://github.com/fonttools/fontbakery/issues/1489
        "Failure to handle font family with 3 words in it"
        """
        # TODO (M Foley) this case is insane. We should just fix the fonts
        # and drop this function
        if s[-2:] == "of":
            return s[:-2] + " of"
        else:
            return s

    familyname = " ".join(map(of_special_case, familyname.split(" ")))
    return familyname


@condition(Font)
def VTT_hinted(font):
    # it seems that VTT is the only program that generates a TSI5 table
    return "TSI5" in font.ttFont


@condition(CheckRunContext)
def gfonts_repo_structure(self):
    """The family at the given font path
    follows the files and directory structure
    typical of a font project hosted on
    the Google Fonts repo on GitHub?"""

    # FIXME: Improve this with more details
    #        about the expected structure.
    abspath = os.path.abspath(self.fonts[0].file)
    return abspath.split(os.path.sep)[-3] in ["ufl", "ofl", "apache"]


@condition(CheckRunContext)
def production_metadata(context):
    """Get the Google Fonts production metadata"""
    if not context.network:
        return

    import requests

    meta_url = "http://fonts.google.com/metadata/fonts"
    return requests.get(meta_url, timeout=context.config.get("timeout")).json()


@condition(Font)
def upstream_yaml(font):
    fp = os.path.join(font.family_directory, "upstream.yaml")
    if not os.path.isfile(fp):
        return None
    return yaml.load(open(fp, "r", encoding="utf-8"), yaml.FullLoader)


@condition(Font)
def is_noto(font):
    return font.font_familyname.startswith("Noto ")


# Note that this is not a condition!
def expected_font_names(ttFont, ttFonts):
    from axisregistry import build_name_table, build_fvar_instances, build_stat
    from copy import deepcopy

    siblings = [f for f in ttFonts if f != ttFont]
    font_cp = TTFont()
    for table in ["fvar", "name", "STAT", "OS/2", "post", "head"]:
        if table in ttFont:
            font_cp[table] = deepcopy(ttFont[table])
    build_name_table(font_cp, siblings=siblings)
    if "fvar" in font_cp:
        build_fvar_instances(font_cp)
        build_stat(font_cp, siblings)
    return font_cp


@condition(Font)
def is_claiming_to_be_cjk_font(font):
    """Test font object to confirm that it meets our definition of a CJK font file.

    We do this in two ways: in some cases, we are testing the *metadata*,
    i.e. what the font claims about itself, in which case the definition is
    met if any of the following conditions are True:

      1. The font has a CJK code page bit set in the OS/2 table
      2. The font has a CJK Unicode range bit set in the OS/2 table

    See below for another way of testing this.
    """
    from fontbakery.constants import (
        CJK_CODEPAGE_BITS,
        CJK_UNICODE_RANGE_BITS,
    )

    if not font.has_os2_table:
        return

    os2 = font.ttFont["OS/2"]

    # OS/2 code page checks
    for _, bit in CJK_CODEPAGE_BITS.items():
        if os2.ulCodePageRange1 & (1 << bit):
            return True

    # OS/2 Unicode range checks
    for _, bit in CJK_UNICODE_RANGE_BITS.items():
        if bit in range(0, 32):
            if os2.ulUnicodeRange1 & (1 << bit):
                return True

        elif bit in range(32, 64):
            if os2.ulUnicodeRange2 & (1 << (bit - 32)):
                return True

        elif bit in range(64, 96):
            if os2.ulUnicodeRange3 & (1 << (bit - 64)):
                return True

    # default, return False if the above checks did not identify a CJK font
    return False
