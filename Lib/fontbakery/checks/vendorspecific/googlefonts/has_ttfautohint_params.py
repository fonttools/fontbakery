import re

from fontbakery.prelude import check, Message, PASS, FAIL, SKIP
from fontbakery.constants import NameID


@check(
    id="googlefonts/has_ttfautohint_params",
    proposal="https://github.com/fonttools/fontbakery/issues/1773",
    rationale="""
        It is critically important that all static TTFs in the Google Fonts API
        which were autohinted with ttfautohint store their TTFAutohint args in
        the 'name' table, so that an automated solution can be made to
        replicate the hinting on subsets, etc.
    """,
)
def check_has_ttfautohint_params(ttFont):
    """Font has ttfautohint params?"""
    from fontbakery.utils import get_name_entry_strings

    def ttfautohint_version(value):
        # example string:
        # 'Version 1.000; ttfautohint (v0.93) -l 8 -r 50 -G 200 -x 14 -w "G"
        results = re.search(r"ttfautohint \(v(.*)\) ([^;]*)", value)
        if results:
            return results.group(1), results.group(2)

    version_strings = get_name_entry_strings(ttFont, NameID.VERSION_STRING)
    passed = False
    for vstring in version_strings:
        values = ttfautohint_version(vstring)
        if values:
            ttfa_version, params = values
            if params:
                passed = True
                yield PASS, Message("ok", f"Font has ttfautohint params ({params})")
        else:
            passed = True
            yield SKIP, Message(
                "not-hinted",
                "Font appears to our heuristic as not hinted using ttfautohint.",
            )

    if not passed:
        yield FAIL, Message(
            "lacks-ttfa-params",
            "Font is lacking ttfautohint params on its"
            " version strings on the name table.",
        )
