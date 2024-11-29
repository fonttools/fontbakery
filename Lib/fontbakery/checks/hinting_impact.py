import os
from io import BytesIO
import tempfile

from dehinter.font import dehint
from fontTools.subset import main as pyftsubset
from fontTools.ttLib import TTFont

from fontbakery.prelude import check, Message, INFO
from fontbakery.testable import Font
from fontbakery.utils import filesize_formatting


def hinting_stats(font: Font):
    """Return file size differences for a hinted font compared
    to an dehinted version of same file.
    """
    hinted_size = os.stat(font.file).st_size
    ttFont = TTFont(font.file)  # Use our own copy since we will dehint it

    if font.is_ttf:
        dehinted_buffer = BytesIO()
        dehint(ttFont, verbose=False)
        ttFont.save(dehinted_buffer)
        dehinted_buffer.seek(0)
        dehinted_size = len(dehinted_buffer.read())
    elif font.is_cff or font.is_cff2:
        ext = os.path.splitext(font.file)[1]
        tmp_dir = tempfile.mkdtemp()
        tmp = os.path.join(tmp_dir, "dehinted%s" % ext)

        args = [
            font.file,
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
            "--output-file=%s" % tmp,
        ]
        pyftsubset(args)

        dehinted_size = os.stat(tmp).st_size
        os.remove(tmp)
        os.rmdir(tmp_dir)
    else:
        return None

    return {
        "dehinted_size": dehinted_size,
        "hinted_size": hinted_size,
    }


@check(
    id="hinting_impact",
    rationale="""
        This check is merely informative, displaying an useful comparison of filesizes
        of hinted versus unhinted font files.
    """,
    proposal="https://github.com/fonttools/fontbakery/issues/4829",  # legacy check
)
def check_hinting_impact(font):
    """Show hinting filesize impact."""
    stats = hinting_stats(font)
    hinted = stats["hinted_size"]
    dehinted = stats["dehinted_size"]
    increase = hinted - dehinted
    change = (float(hinted) / dehinted - 1) * 100

    hinted_size = filesize_formatting(hinted)
    dehinted_size = filesize_formatting(dehinted)
    increase = filesize_formatting(increase)

    yield INFO, Message(
        "size-impact",
        f"Hinting filesize impact:\n"
        f"\n"
        f" |               | {font.file}     |\n"
        f" |:------------- | ---------------:|\n"
        f" | Dehinted Size | {dehinted_size} |\n"
        f" | Hinted Size   | {hinted_size}   |\n"
        f" | Increase      | {increase}      |\n"
        f" | Change        | {change:.1f} %  |\n",
    )
