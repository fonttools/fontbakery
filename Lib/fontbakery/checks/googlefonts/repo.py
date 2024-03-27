import os

from fontbakery.constants import NameID
from fontbakery.testable import Font
from fontbakery.prelude import check, Message, FAIL, WARN, SKIP
from fontbakery.utils import bullet_list


@check(
    id="com.google.fonts/check/repo/fb_report",
    conditions=["family_directory"],
    rationale="""
        A FontBakery report is ephemeral and so should be used for posting issues on a
        bug-tracker instead of being hosted in the font project repository.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2888",
)
def com_google_fonts_check_repo_fb_report(family_directory):
    """A font repository should not include FontBakery report files"""
    from fontbakery.utils import filenames_ending_in

    has_report_files = any(
        [
            f
            for f in filenames_ending_in(".json", family_directory)
            if '"result"' in open(f, encoding="utf-8").read()
        ]
    )
    if has_report_files:
        yield WARN, Message(
            "fb-report",
            "There's no need to keep a copy of FontBakery reports in the"
            " repository, since they are ephemeral; FontBakery has"
            " a 'github markdown' output mode to make it easy to file"
            " reports as issues.",
        )


@check(
    id="com.google.fonts/check/repo/upstream_yaml_has_required_fields",
    rationale="""
        If a family has been pushed using the gftools packager, we must check that all
        the required fields in the upstream.yaml file have been populated.
    """,
    conditions=["upstream_yaml"],
    severity=10,
    proposal="https://github.com/fonttools/fontbakery/issues/3338",
)
def com_google_fonts_check_repo_upstream_yaml_has_required_fields(upstream_yaml):
    """Check upstream.yaml file contains all required fields"""
    required_fields = set(["branch", "files"])
    upstream_fields = set(upstream_yaml.keys())

    missing_fields = required_fields - upstream_fields
    if missing_fields:
        yield FAIL, Message(
            "missing-fields",
            f"The upstream.yaml file is missing the following fields:"
            f" {list(missing_fields)}",
        )


@check(
    id="com.google.fonts/check/repo/zip_files",
    conditions=["family_directory"],
    rationale="""
        Sometimes people check in ZIPs into their font project repositories. While we
        accept the practice of checking in binaries, we believe that a ZIP is a step
        too far ;)

        Note: a source purist position is that only source files and build scripts
        should be checked in.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2903",
)
def com_google_fonts_check_repo_zip_files(family_directory, config):
    """A font repository should not include ZIP files"""
    from fontbakery.utils import filenames_ending_in, pretty_print_list

    COMMON_ZIP_EXTENSIONS = [".zip", ".7z", ".rar"]
    zip_files = []
    for ext in COMMON_ZIP_EXTENSIONS:
        zip_files.extend(filenames_ending_in(ext, family_directory))

    if zip_files:
        files_list = pretty_print_list(config, zip_files, sep="\n\t* ")
        yield FAIL, Message(
            "zip-files",
            f"Please do not host ZIP files on the project repository."
            f" These files were detected:\n"
            f"\t* {files_list}",
        )


@check(
    id="com.google.fonts/check/repo/sample_image",
    rationale="""
        In order to showcase what a font family looks like, the project's README.md
        file should ideally include a sample image and highlight it in the upper
        portion of the document, no more than 10 lines away from the top of the file.
    """,
    conditions=["readme_contents", "readme_directory"],
    proposal="https://github.com/fonttools/fontbakery/issues/2898",
)
def com_google_fonts_check_repo_sample_image(readme_contents, readme_directory, config):
    """Check README.md has a sample image."""
    import glob
    import re

    image_path = False
    line_number = 0
    for line in readme_contents.split("\n"):
        if line.strip() == "":
            continue

        line_number += 1
        # We're looking for something like this:
        # ![Raleway font sample](documents/raleway-promo.jpg)
        # And we accept both png and jpg files
        result = re.match(r"\!\[.*\]\((.*\.(png|jpg))\)", line)
        if result:
            image_path = os.path.join(readme_directory, result[1].replace("/", os.sep))
            break

    local_image_files = glob.glob(os.path.join(readme_directory, "**/*.[jp][np]g"))

    if local_image_files:
        sample_tip = local_image_files[0]
    else:
        sample_tip = "samples/some-sample-image.jpg"
    MARKDOWN_IMAGE_SYNTAX_TIP = (
        f"You can use something like this:\n\n" f"\t![font sample]({sample_tip})"
    )

    if image_path:
        if image_path not in local_image_files:
            yield FAIL, Message(
                "image-missing",
                f"The referenced sample image could not be found:"
                f" {os.path.join(readme_directory, image_path)}\n",
            )
        else:
            if line_number >= 10:
                yield WARN, Message(
                    "not-ideal-placement",
                    "Please consider placing the sample image closer"
                    " to the top of the README document so that it is"
                    " more immediately viewed by readers.\n",
                )
    else:  # if no image reference was found on README.md:
        if local_image_files:
            yield WARN, Message(
                "image-not-displayed",
                f"Even though the README.md file does not display"
                f" a font sample image, a few image files were found:\n\n"
                f"{bullet_list(config, local_image_files)}\n"
                f"\n"
                f"Please consider including one of those images on the README.\n"
                f"{MARKDOWN_IMAGE_SYNTAX_TIP}\n",
            )
        else:
            yield WARN, Message(
                "no-sample",
                f"Please add a font sample image to the README.md file.\n"
                f"{MARKDOWN_IMAGE_SYNTAX_TIP}\n",
            )


@check(
    id="com.google.fonts/check/repo/vf_has_static_fonts",
    conditions=["family_directory", "gfonts_repo_structure"],
    rationale="""
        Variable font family directories kept in the google/fonts git repo may include
        a static/ subdir containing static fonts, if manual hinting is used on
        these fonts. Otherwise, the directory should be removed.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2654",
)
def com_google_fonts_check_repo_vf_has_static_fonts(family_directory):
    """A static fonts directory, if present, must contain manually hinted fonts"""
    from fontbakery.utils import get_name_entry_strings

    def manually_hinted(font):
        if not font.is_hinted:
            return False
        if font.VTT_hinted:
            return True
        name_strings = get_name_entry_strings(font.ttFont, NameID.VERSION_STRING)
        if any("ttfautohint" in name for name in name_strings):
            return False
        return True

    static_dir = os.path.join(family_directory, "static")
    if os.path.exists(static_dir):
        static_fonts = [
            Font(os.path.join(static_dir, f))
            for f in os.listdir(static_dir)
            if f.endswith(".ttf")
        ]
        if not static_fonts:
            # it is all fine!
            return

        if not all(manually_hinted(font) for font in static_fonts):
            yield WARN, Message(
                "not-manually-hinted",
                'There is a "static" dir but it contains fonts which are not '
                "manually hinted. Delete the directory.",
            )
            return


@check(
    id="com.google.fonts/check/repo/dirname_matches_nameid_1",
    conditions=["gfonts_repo_structure"],
    proposal="https://github.com/fonttools/fontbakery/issues/2302",
    rationale="""
        For static fonts, we expect to name the directory in google/fonts
        according to the NameID 1 of the regular font, all lower case with
        no hyphens or spaces. This check verifies that the directory
        name matches our expectations.
    """,
)
def com_google_fonts_check_repo_dirname_match_nameid_1(fonts):
    """Directory name in GFonts repo structure must
    match NameID 1 of the regular."""
    from fontTools.ttLib import TTFont
    from fontbakery.utils import get_name_entry_strings, get_regular

    if any(f.is_variable_font for f in fonts):
        yield SKIP, Message(
            "variable-exempt", "Variable fonts are exempt from this check."
        )
        return

    regular = get_regular(fonts)
    if not regular:
        yield FAIL, Message(
            "lacks-regular",
            "The font seems to lack a regular."
            " If family consists of a single-weight non-Regular style only,"
            " consider the Google Fonts specs for this case:"
            " https://github.com/googlefonts/gf-docs/tree/main/Spec#single-weight-families",  # noqa:E501 pylint:disable=C0301
        )
        return

    entry = get_name_entry_strings(TTFont(regular.file), NameID.FONT_FAMILY_NAME)[0]
    expected = entry.lower()
    expected = "".join(expected.split(" "))
    expected = "".join(expected.split("-"))

    _, familypath, _ = os.path.abspath(regular.file).split(os.path.sep)[-3:]
    if familypath != expected:
        yield FAIL, Message(
            "mismatch",
            f"Family name on the name table ('{entry}') does not match"
            f" directory name in the repo structure ('{familypath}')."
            f" Expected '{expected}'.",
        )
