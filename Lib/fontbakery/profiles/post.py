from fontbakery.callable import check
from fontbakery.status import FAIL, PASS, WARN
from fontbakery.message import Message
# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('is_ttf', ))
]

@check(
    id = 'com.google.fonts/check/family/underline_thickness',
    rationale = """
        Dave C Lemon (Adobe Type Team) recommends setting the underline thickness to be consistent across the family.

        If thicknesses are not family consistent, words set on the same line which have different styles look strange.
    """,
    proposal = 'legacy:check/008',
    misc_metadata = {
        'affects': [('InDesign', 'unspecified')]
    }
)
def com_google_fonts_check_family_underline_thickness(ttFonts):
    """Fonts have consistent underline thickness?"""
    underTs = {}
    underlineThickness = None
    failed = False
    for ttfont in ttFonts:
        fontname = ttfont.reader.file.name
        # stylename = style(fontname)
        ut = ttfont['post'].underlineThickness
        underTs[fontname] = ut
        if underlineThickness is None:
            underlineThickness = ut
        if ut != underlineThickness:
            failed = True

    if failed:
        msg = ("Thickness of the underline is not"
               " the same across this family. In order to fix this,"
               " please make sure that the underlineThickness value"
               " is the same in the 'post' table of all of this family"
               " font files.\n"
               "Detected underlineThickness values are:\n")
        for style in underTs.keys():
            msg += f"\t{style}: {underTs[style]}\n"
        yield FAIL, Message("inconsistent-underline-thickness", msg)
    else:
        yield PASS, "Fonts have consistent underline thickness."


@check(
    id = 'com.google.fonts/check/post_table_version',
    rationale = """
        Format 2.5 of the 'post' table was deprecated in OpenType 1.3 and
        should not be used.

        According to Thomas Phinney, the possible problem with post format 3
        is that under the right combination of circumstances, one can generate
        PDF from a font with a post format 3 table, and not have accurate backing
        store for any text that has non-default glyphs for a given codepoint.
        
        It will look fine but not be searchable. This can affect Latin text with
        high-end typography, and some complex script writing systems, especially
        with higher-quality fonts. Those circumstances generally involve creating
        a PDF by first printing a PostScript stream to disk, and then creating a
        PDF from that stream without reference to the original source document.
        There are some workflows where this applies,but these are not common
        use cases.

        Apple recommends against use of post format version 4 as "no longer
        necessary and should be avoided". Please see the Apple TrueType reference
        documentation for additional details.
         
        https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6post.html

        Acceptable post format versions are 2 and 3 for TTF and OTF CFF2 builds,
        and post format 3 for CFF builds.
    """,
    proposal = ['legacy:check/015',
                'https://github.com/google/fonts/issues/215',
                'https://github.com/googlefonts/fontbakery/issues/2638',
                'https://github.com/googlefonts/fontbakery/issues/3635']
)
def com_google_fonts_check_post_table_version(ttFont):
    """Font has correct post table version?"""
    formatType = ttFont['post'].formatType
    is_cff = "CFF " in ttFont

    if is_cff and formatType != 3:
        yield FAIL, \
              Message("post-table-version",
                      "CFF fonts must contain post format 3 table.")
    elif not is_cff and formatType == 3:
        yield WARN, \
              Message("post-table-version",
                      "Post table format 3 use has niche use case problems."
                      "Please review the check rationale for additional details.")
    elif formatType == 2.5:
        yield FAIL, \
              Message("post-table-version",
                      "Post format 2.5 was deprecated in OpenType 1.3 and should" 
                      "not be used.")
    elif formatType == 4:
        yield FAIL, \
              Message("post-table-version",
                      "According to Apple documentation, post format 4 tables are" 
                      "no longer necessary and should not be used.")
    else:
        yield PASS, f"Font has an acceptable post format {formatType} table version."


@check(
    id = 'com.google.fonts/check/italic_angle',
    conditions = ['style'],
    rationale = """
        The 'post' table italicAngle property should be a reasonable amount, likely
        not more than -20°, never more than -30°, and never greater than 0°. Note that
        in the OpenType specification, the value is negative for a lean rightwards.

        https://docs.microsoft.com/en-us/typography/opentype/spec/post
    """,
    proposal = 'legacy:check/130'
)
def com_google_fonts_check_italic_angle(ttFont, style):
    """Checking post.italicAngle value."""
    failed = False
    value = ttFont["post"].italicAngle

    # Checking that italicAngle <= 0
    if value > 0:
        failed = True
        yield FAIL,\
              Message("positive",
                      (f"The value of post.italicAngle is positive, which"
                       f" is likely a mistake and should become negative,"
                       f" from {value} to {-value}."))

    # Checking that italicAngle is less than 20° (not good) or 30° (bad)
    # Also note we invert the value to check it in a clear way
    if abs(value) > 30:
        failed = True
        yield WARN,\
              Message("over-minus30-degrees",
                      (f"The value of post.italicAngle ({value}) is very high"
                       f" (over -30°!) and should be confirmed."))
    elif abs(value) > 20:
        failed = True
        yield WARN,\
              Message("over-minus20-degrees",
                      (f"The value of post.italicAngle ({value}) seems very high"
                       f" (over -20°!) and should be confirmed."))


    # Checking if italicAngle matches font style:
    if "Italic" in style:
        if ttFont['post'].italicAngle == 0:
            failed = True
            yield FAIL,\
                  Message("zero-italic",
                          ("Font is italic, so post.italicAngle"
                           " should be non-zero."))
    else:
        if ttFont["post"].italicAngle != 0:
            failed = True
            yield FAIL,\
                  Message("non-zero-normal",
                          ("Font is not italic, so post.italicAngle"
                           " should be equal to zero."))

    if not failed:
        yield PASS, (f'Value of post.italicAngle is {value}'
                     f' with style="{style}".')
