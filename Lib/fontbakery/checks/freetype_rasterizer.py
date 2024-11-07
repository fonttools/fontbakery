import freetype
from freetype.ft_errors import FT_Exception

from fontbakery.prelude import PASS, FAIL, Message, check


@check(
    id="freetype_rasterizer",
    conditions=["ttFont"],
    severity=10,
    rationale="""
        Malformed fonts can cause FreeType to crash.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/3642",
)
def check_freetype_rasterizer(font):
    """Ensure that the font can be rasterized by FreeType."""

    try:
        face = freetype.Face(font.file)
        face.set_char_size(48 * 64)
        face.load_char("✅")  # any character can be used here

    except FT_Exception as err:
        yield FAIL, Message(
            "freetype-crash", f"Font caused FreeType to crash with this error: {err}"
        )
    else:
        yield PASS, "Font can be rasterized by FreeType."
