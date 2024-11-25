import os

from fontbakery.constants import NameID
from fontbakery.testable import Font
from fontbakery.prelude import check, Message, WARN


@check(
    id="googlefonts/repo/vf_has_static_fonts",
    conditions=["family_directory", "gfonts_repo_structure"],
    rationale="""
        Variable font family directories kept in the google/fonts git repo may include
        a static/ subdir containing static fonts, if manual hinting is used on
        these fonts. Otherwise, the directory should be removed.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/2654",
)
def check_repo_vf_has_static_fonts(family_directory):
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
