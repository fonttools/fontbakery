import os
import re
import yaml

from fontbakery.callable import condition
from fontbakery.constants import (
    NameID,
    PlatformID,
    UnicodeEncodingID,
    WindowsLanguageID
)

# -------------------------------------------------------------------
# FIXME! Redundant with @condition canonical_stylename(font)?
@condition
def style(font):
    """Determine font style from canonical filename."""
    from fontbakery.constants import STATIC_STYLE_NAMES
    filename = os.path.basename(font)
    if '-' in filename:
        stylename = os.path.splitext(filename)[0].split('-')[1]
        if stylename in [name.replace(' ', '') for name in STATIC_STYLE_NAMES]:
            return stylename
    return None


@condition
def RIBBI_ttFonts(ttFonts):
    from fontbakery.constants import RIBBI_STYLE_NAMES
    return [ttFont for ttFont in ttFonts
            if style(ttFont.reader.file.name) in RIBBI_STYLE_NAMES]


@condition
def glyphsFile(glyphs_file):
    import glyphsLib
    return glyphsLib.load(open(glyphs_file))


@condition
def style_with_spaces(font):
    """Stylename with spaces (derived from a canonical filename)."""
    if style(font):
        return style(font).replace('Italic',
                                   ' Italic').strip()

@condition
def expected_style(ttFont):
    from fontbakery.parse import style_parse
    return style_parse(ttFont)


@condition
def expected_os2_weight(style):
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
    if not style:
        return None
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
        "Black": 900
    }
    if style == "Italic":
        weight_name = "Regular"
    elif style.endswith("Italic"):
        weight_name = style.replace("Italic", "")
    else:
        weight_name = style

    expected = GF_API_WEIGHTS[weight_name]
    return weight_name, expected


@condition
def stylenames_are_canonical(fonts):
    """ Are all font files named canonically ? """
    for font in fonts:
        if not canonical_stylename(font):
            return False
    # otherwise:
    return True


@condition
def canonical_stylename(font):
    """ Returns the canonical stylename of a given font. """
    from fontbakery.utils import suffix
    from fontbakery.constants import (STATIC_STYLE_NAMES,
                                      VARFONT_SUFFIXES)
    from .shared_conditions import is_variable_font
    from fontTools.ttLib import TTFont

    # remove spaces in style names
    valid_style_suffixes = [name.replace(' ', '') for name in STATIC_STYLE_NAMES]

    filename = os.path.basename(font)
    basename = os.path.splitext(filename)[0]
    s = suffix(font)
    varfont = os.path.exists(font) and is_variable_font(TTFont(font))
    if ('-' in basename and
        (s in VARFONT_SUFFIXES and varfont)
        or (s in valid_style_suffixes and not varfont)):
        return s


@condition
def descfile(font):
    """Get the path of the DESCRIPTION file of a given font project."""
    if font:
        directory = os.path.dirname(font)
        descfilepath = os.path.join(directory, "DESCRIPTION.en_us.html")
        if os.path.exists(descfilepath):
            return descfilepath


@condition
def description(descfile):
    """Get the contents of the DESCRIPTION file of a font project."""
    if not descfile:
        return
    import io
    return io.open(descfile, "r", encoding="utf-8").read()


@condition
def readme_directory(readme_md):
    if not readme_md:
        return
    if isinstance(readme_md, list):
        # It makes no sense to deal with more than a single README.md file
        # This here is just a quirk of the way we handle fontbakery inputs nowadays.
        readme_md = readme_md[0]
    return os.path.dirname(readme_md)


@condition
def readme_contents(readme_md):
    """Get the contents of the README.md file of a font project."""
    if not readme_md:
        return
    if isinstance(readme_md, list):
        readme_md = readme_md[0]        # quirk
    return open(readme_md, "r", encoding="utf-8").read()


@condition
def metadata_file(family_directory,
                  metadata_pb=None):
    if metadata_pb:
        if isinstance(metadata_pb, list):
            metadata_pb = metadata_pb[0]        # quirk

        return metadata_pb

    elif family_directory:
        pb_file = os.path.join(family_directory, "METADATA.pb")
        if os.path.exists(pb_file):
            return pb_file

@condition
def family_metadata(metadata_file):
    if not metadata_file:
        return

    from google.protobuf import text_format
    from fontbakery.utils import get_FamilyProto_Message
    try:
        return get_FamilyProto_Message(metadata_file)
    except text_format.ParseError:
        return None


@condition
def registered_vendor_ids():
    """Get a list of vendor IDs from Microsoft's website."""
    from bs4 import BeautifulSoup
    from pkg_resources import resource_filename

    registered_vendor_ids = {}
    CACHED = resource_filename('fontbakery',
                               'data/fontbakery-microsoft-vendorlist.cache')
    content = open(CACHED, encoding='utf-8').read()
    # Strip all <A> HTML tags from the raw HTML. The current page contains a
    # closing </A> for which no opening <A> is present, which causes
    # beautifulsoup to silently stop processing that section from the error
    # onwards. We're not using the href's anyway.
    content = re.sub("<a[^>]*>", "", content, flags=re.IGNORECASE)
    content = re.sub("</a>", "", content, flags=re.IGNORECASE)
    soup = BeautifulSoup(content, 'html.parser')

    IDs = [chr(c + ord('a')) for c in range(ord('z') - ord('a') + 1)]
    IDs.append("0-9-")

    for section_id in IDs:
        section = soup.find('h2', {'id': section_id})
        table = section.find_next_sibling('table')
        if not table: continue

        #print ("table: '{}'".format(table))
        for row in table.findAll('tr'):
            #print("ROW: '{}'".format(row))
            cells = row.findAll('td')
            if not cells:
                continue

            labels = [label for label in cells[1].stripped_strings]

            # pad the code to make sure it is a 4 char string,
            # otherwise eg "CF  " will not be matched to "CF"
            code = cells[0].string.strip()
            code = code + (4 - len(code)) * ' '
            registered_vendor_ids[code] = labels[0]

            # Do the same with NULL-padding:
            code = cells[0].string.strip()
            code = code + (4 - len(code)) * chr(0)
            registered_vendor_ids[code] = labels[0]


    return registered_vendor_ids


def git_rootdir(family_dir):
    if not family_dir:
        return None

    original_dir = os.getcwd()
    root_dir = None
    try:
        import subprocess
        os.chdir(family_dir)
        git_cmd = [
            "git", "rev-parse", "--show-toplevel"
        ]
        git_output = subprocess.check_output(git_cmd, stderr=subprocess.STDOUT)
        root_dir = git_output.decode("utf-8").strip()

    except (OSError, IOError, subprocess.CalledProcessError):
        pass # Not a git repo, or git is not installed.

    os.chdir(original_dir)
    return root_dir


@condition
def licenses(family_directory):
    """Get a list of paths for every license
       file found in a font project."""
    found = []
    search_paths = [family_directory]
    gitroot = git_rootdir(family_directory)
    if gitroot and gitroot not in search_paths:
        search_paths.append(gitroot)

    for directory in search_paths:
        if directory:
            for license in ['OFL.txt', 'LICENSE.txt']:
                license_path = os.path.join(directory, license)
                if os.path.exists(license_path):
                    found.append(license_path)
    return found


@condition
def license_contents(license_path):
    if license_path:
        return open(license_path).read()


@condition
def license_path(licenses):
    """Get license path."""
    # This assumes that a repo can have multiple license files
    # and they're all the same.
    # FIXME: We should have a fontbakery check for that, though!
    if licenses and len(licenses) > 0:
        return licenses[0]


@condition
def license(license_path):
    """Get license filename."""
    if license_path:
        return os.path.basename(license_path)

@condition
def is_ofl(license):
    return license and "OFL" in license


@condition
def familyname(font):
    filename = os.path.basename(font)
    filename_base = os.path.splitext(filename)[0]
    if '-' in filename_base:
        return filename_base.split('-')[0]
    # Handle VFs e.g Inconsolata[wdth,wght] --> Inconsolata
    elif "[" in filename_base:
        return filename_base.split("[")[0]
    else:
        return filename_base


@condition
def hinting_stats(font):
    """
    Return file size differences for a hinted font compared to an dehinted version of same file
    """
    from io import BytesIO
    from dehinter.font import dehint
    from fontTools.ttLib import TTFont
    from fontTools.subset import main as pyftsubset
    from fontbakery.profiles.shared_conditions import (is_ttf,
                                                       is_cff,
                                                       is_cff2)

    hinted_size = os.stat(font).st_size
    ttFont = TTFont(font)

    if is_ttf(ttFont):
        dehinted_buffer = BytesIO()
        dehint(ttFont, verbose=False)
        ttFont.save(dehinted_buffer)
        dehinted_buffer.seek(0)
        dehinted_size = len(dehinted_buffer.read())
    elif is_cff(ttFont) or is_cff2(ttFont):
        ext = os.path.splitext(font)[1]
        tmp = font.replace(ext, "-tmp-dehinted%s" % ext)
        args = [font,
                "--no-hinting",
                "--glyphs=*",
                "--ignore-missing-glyphs",
                "--no-notdef-glyph",
                "--no-recommended-glyphs",
                "--no-layout-closure",
                "--layout-features=*",
                "--no-desubroutinize",
                "--name-languages=*",
                "--glyph-names",
                "--no-prune-unicode-ranges",
                "--output-file=%s" % tmp]
        pyftsubset(args)

        dehinted_size = os.stat(tmp).st_size
        os.remove(tmp)

    else:
        return None

    return {
        "dehinted_size": dehinted_size,
        "hinted_size": hinted_size,
    }


@condition
def listed_on_gfonts_api(familyname):
    if not familyname:
        return False

    from fontbakery.utils import split_camel_case
    # Some families such as "Libre Calson Text" have camelcased filenames
    # ("LibreCalsonText-Regular.ttf") and require us to split in order
    # to find it in the GFonts metadata:
    from_camelcased_name = split_camel_case(familyname)

    for item in production_metadata()["familyMetadataList"]:
        if item["family"] == familyname or \
           item["family"] == from_camelcased_name:
            return True

    return False


@condition
def has_regular_style(family_metadata):
    fonts = family_metadata.fonts if family_metadata else []
    for f in fonts:
        if f.weight == 400 and f.style == "normal":
            return True
    return False


@condition
def font_metadata(family_metadata, font):
    if not family_metadata:
        return

    for f in family_metadata.fonts:
        if font.endswith(f.filename):
            return f


@condition
def font_familynames(ttFont):
    from fontbakery.utils import get_name_entry_strings
    return get_name_entry_strings(ttFont, NameID.FONT_FAMILY_NAME)


@condition
def typographic_familynames(ttFont):
    from fontbakery.utils import get_name_entry_strings
    return get_name_entry_strings(ttFont, NameID.TYPOGRAPHIC_FAMILY_NAME)


@condition
def font_familyname(font_familynames):
    # This assumes that all familyname
    # name table entries are identical.
    # FIX-ME: Maybe we should have a check for that.
    #         Have we ever seen this kind of
    #         problem in the wild, though ?
    return font_familynames[0]


# TODO: Design special case handling mechanism:
# https://github.com/googlefonts/fontbakery/issues/1540
# TODO: Improve camelcase check result explanation and whitelisting process:
#https://github.com/googlefonts/fontbakery/issues/3270
@condition
def camelcased_familyname_exception(familyname):
    '''In general, we would not like to have camel-cased
       familynames but there are a few exceptions to that
       rule, that we keep listed here, for now.
    '''
    for exception in [
        "3D", # seen in "Rock 3D"
        "ABeeZee",
        "BenchNine",
        "BhuTuka", # seen in "BhuTuka Expanded One"
        "DotGothic", # seen in "DotGothic16"
        "FakeFont",
        "JetBrains", # seen in "JetBrains Mono"
        "McLaren",
        "MedievalSharp",
        "RocknRoll", # seen in "RocknRoll One"
        "UnifrakturCook",
        "UnifrakturMaguntia",
        "MonteCarlo",
        "WindSong",
    ]:
        if exception in familyname:
            return True

@condition
def rfn_exception(familyname):
    '''These are the very few font families where we accept usage of
       a Reserved Font Name. These are typically fonts that had already
       been published previously with an RFN, or fonts which benefit from
       an agreement with Google Fonts.
    '''
    RNF_EXCEPTIONS = [] # For now we'll leave this empty because the
                        # actual long list of familynames we had here
                        # still needs to be more carefully reviewed.
                        # See https://github.com/googlefonts/fontbakery/issues/3612

    for exception in RNF_EXCEPTIONS:
        if exception in familyname:
            return True


@condition
def remote_styles(familyname_with_spaces):
    """Get a dictionary of TTFont objects of all font files of
       a given family as currently hosted at Google Fonts.
    """

    def download_family_from_Google_Fonts(familyname):
        """Return a zipfile containing a font family hosted on fonts.google.com"""
        from zipfile import ZipFile
        from fontbakery.utils import download_file
        url_prefix = 'https://fonts.google.com/download?family='
        url = '{}{}'.format(url_prefix, familyname.replace(' ', '+'))
        return ZipFile(download_file(url))  # pylint: disable=R1732


    def fonts_from_zip(zipfile):
        '''return a list of fontTools TTFonts'''
        from fontTools.ttLib import TTFont
        from io import BytesIO
        fonts = []
        for file_name in zipfile.namelist():
            if file_name.lower().endswith(".ttf"):
                file_obj = BytesIO(zipfile.open(file_name).read())
                fonts.append([file_name, TTFont(file_obj)])
        return fonts

    if not listed_on_gfonts_api(familyname_with_spaces):
        return None

    remote_fonts_zip = download_family_from_Google_Fonts(familyname_with_spaces)
    rstyles = {}

    for remote_filename, remote_font in fonts_from_zip(remote_fonts_zip):
        remote_style = os.path.splitext(remote_filename)[0]
        if '-' in remote_style:
            remote_style = remote_style.split('-')[1]
        rstyles[remote_style] = remote_font
    return rstyles


@condition
def regular_remote_style(remote_styles):
    from .shared_conditions import is_variable_font, get_instance_axis_value
    if not remote_styles:
        return None
    if "Regular" in remote_styles:
        return remote_styles["Regular"]

    for style, font in remote_styles.items():
        if is_variable_font(font):
            if get_instance_axis_value(font, "Regular", "wght"):
                return font
    return list(remote_styles.items())[0][1]


@condition
def regular_ttFont(ttFonts):
    from .shared_conditions import is_variable_font, get_instance_axis_value
    for ttFont in ttFonts:
        if "-Regular." in os.path.basename(ttFont.reader.file.name):
            return ttFont
        nametable = ttFont['name']
        sub_family = nametable.getName(NameID.FONT_SUBFAMILY_NAME,
                                       PlatformID.WINDOWS,
                                       UnicodeEncodingID.UNICODE_1_1,
                                       WindowsLanguageID.ENGLISH_USA)
        typo_sub_family = nametable.getName(NameID.TYPOGRAPHIC_SUBFAMILY_NAME,
                                            PlatformID.WINDOWS,
                                            UnicodeEncodingID.UNICODE_1_1,
                                            WindowsLanguageID.ENGLISH_USA)
        if sub_family and sub_family.toUnicode() == "Regular" and not typo_sub_family:
            return ttFont
        if is_variable_font(ttFont):
            if get_instance_axis_value(ttFont, "Regular", "wght"):
                return ttFont
    return None


@condition
def api_gfonts_ttFont(style, remote_styles):
    """Get a TTFont object of a font downloaded from Google Fonts
       corresponding to the given TTFont object of
       a local font being checked.
    """
    if remote_styles and style in remote_styles:
        return remote_styles[style]


@condition
def github_gfonts_ttFont(ttFont, license):
    """Get a TTFont object of a font downloaded
       from Google Fonts git repository.
    """
    if not license:
        return None

    from fontbakery.utils import download_file
    from fontTools.ttLib import TTFont
    from urllib.request import HTTPError
    LICENSE_DIRECTORY = {
        "OFL.txt": "ofl",
        "UFL.txt": "ufl",
        "LICENSE.txt": "apache"
    }
    filename = os.path.basename(ttFont.reader.file.name)
    familyname = filename.split('-')[0].lower()
    url = (f"https://github.com/google/fonts/raw/main"
           f"/{LICENSE_DIRECTORY[license]}/{familyname}/{filename}")
    try:
        fontfile = download_file(url)
        if fontfile:
            return TTFont(fontfile)
    except HTTPError:
        return None


@condition
def github_gfonts_description(ttFont, license):
    """Get the contents of the DESCRIPTION.en_us.html file
       from the google/fonts github repository corresponding
       to a given ttFont.
    """
    if not license:
        return None

    from fontbakery.utils import download_file
    from urllib.request import HTTPError
    LICENSE_DIRECTORY = {
        "OFL.txt": "ofl",
        "UFL.txt": "ufl",
        "LICENSE.txt": "apache"
    }
    filename = os.path.basename(ttFont.reader.file.name)
    familyname = filename.split('-')[0].lower()
    url = (f"https://github.com/google/fonts/raw/main"
           f"/{LICENSE_DIRECTORY[license]}/{familyname}/DESCRIPTION.en_us.html")
    try:
        descfile = download_file(url)
        if descfile:
            return descfile.read().decode('UTF-8')
    except HTTPError:
        return None


@condition
def familyname_with_spaces(familyname):
    """Attempts to build family name from font name.
    For example, HPSimplifiedSans => HP Simplified Sans.
    Args:
      familyname: The name of a font.
    Returns:
      The name of the family that should be in this font.
    """
    # SomethingUpper => Something Upper
    familyname = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', familyname)
    # Font3 => Font 3
    familyname = re.sub('([a-z])([0-9]+)', r'\1 \2', familyname)
    # lookHere => look Here
    familyname = re.sub('([a-z0-9])([A-Z])', r'\1 \2', familyname)

    def of_special_case(s):
        """Special case for family names such as
           MountainsofChristmas which would need to
           have the "of" split apart from "Mountains".

           See also: https://github.com/googlefonts/fontbakery/issues/1489
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


@condition
def VTT_hinted(ttFont):
    # it seems that VTT is the only program that generates a TSI5 table
    return 'TSI5' in ttFont


@condition
def is_hinted(ttFont):
    return "fpgm" in ttFont


@condition
def gfonts_repo_structure(fonts):
    """ The family at the given font path
        follows the files and directory structure
        typical of a font project hosted on
        the Google Fonts repo on GitHub? """
    from fontbakery.utils import get_absolute_path

    # FIXME: Improve this with more details
    #        about the expected structure.
    abspath = get_absolute_path(fonts[0])
    return abspath.split(os.path.sep)[-3] in ["ufl", "ofl", "apache"]


@condition
def production_metadata():
    """Get the Google Fonts production metadata"""
    import json
    import requests
    meta_url = "http://fonts.google.com/metadata/fonts"
    # can't do requests.get("url").json() since request text starts with ")]}'"
    return json.loads(requests.get(meta_url).text[5:])


@condition
def GFAxisRegistry():
    from fontbakery.axes_pb2 import AxisProto
    from fontbakery.utils import get_Protobuf_Message
    from pkg_resources import resource_filename

    def normalize_name(name):
        return ''.join(name.split(' '))

    registry = {}
    def append_AxisMessage(path):
        axis_dict = {"message": get_Protobuf_Message(AxisProto, path),
                     "fallbacks": {}}
        for fb in axis_dict["message"].fallback:
            axis_dict["fallbacks"][normalize_name(fb.name)] = fb.value
        registry[axis_dict["message"].tag] = axis_dict

    for axis in ["casual.textproto",
                 "cursive.textproto",
                 "fill.textproto",
                 "flair.textproto",
                 "grade.textproto",
                 "italic.textproto",
                 "monospace.textproto",
                 "optical_size.textproto",
                 "slant.textproto",
                 "softness.textproto",
                 "volume.textproto",
                 "weight.textproto",
                 "width.textproto",
                 "wonky.textproto",
                 "x_opaque.textproto",
                 "x_transparent_figures.textproto",
                 "x_transparent.textproto",
                 "y_opaque.textproto",
                 "y_transparent_ascender.textproto",
                 "y_transparent_descender.textproto",
                 "y_transparent_figures.textproto",
                 "y_transparent_lowercase.textproto",
                 "y_transparent_uppercase.textproto"]:
        append_AxisMessage(resource_filename('fontbakery', 'data/' + axis))
    return registry


@condition
def upstream_yaml(family_directory):
    fp = os.path.join(family_directory, "upstream.yaml")
    if not os.path.isfile(fp):
        return None
    return yaml.load(open(fp, "r"), yaml.FullLoader)
