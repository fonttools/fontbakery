from fontbakery.checkrunner import Section, PASS, FAIL, WARN, INFO #, ERROR, SKIP
from fontbakery.callable import condition, check
from fontbakery.message import Message
from fontbakery.fonts_profile import profile_factory

profile = profile_factory(default_section=Section("CJK"))


CJK_PROFILE_CHECKS = \
[
    'com.google.fonts/check/cjk/example',
]

# =================================
# Constant Definitions
# =================================

CJK_CODEPAGE_BITS = {
    "JIS/Japan": 17,
    "Chinese: Simplified chars—PRC and Singapore": 18,
    "Korean Wansung": 19,
    "Chinese: Traditional chars—Taiwan and Hong Kong": 20,
    "Korean Johab": 21
}

CJK_UNICODE_RANGE_BITS = {
    'Hangul Jamo': 28,
    'CJK Symbols And Punctuation': 48,
    'Hiragana': 49,
    'Katakana': 50,
    'Bopomofo': 51,
    'Hangul Compatibility Jamo': 52,
    'Enclosed CJK Letters And Months': 54,
    'CJK Compatibility': 55,
    'Hangul Syllables': 56,
    'CJK Unified Ideographs': 59,
    'CJK Strokes': 61,
    'Yi Syllables': 83
}

UNICODE_RANGES = [
    [0x1100, 0x11FF],  # Hangul Jamo
    [0x3000, 0x303F],  # CJK Symbols and Punctuation
    [0x3040, 0x309F],  # Hiragana
    [0x30A0, 0x30FF],  # Katakana
    [0x31F0, 0x31FF],  # Katakana Phonetic Extensions
    [0x3100, 0x312F],  # Bopomofo
    [0x31A0, 0x31BF],  # Bopomofo Extended (Bopomofo)
    [0x3130, 0x318F],  # Hangul Compatibility Jamo
    [0x3200, 0x32FF],  # Enclosed CJK Letters and Months
    [0x3300, 0x33FF],  # CJK Compatibility
    [0xAC00, 0xD7AF],  # Hangul Syllables
    [0x4E00, 0x9FFF],  # CJK Unified Ideographs
    [0x2E80, 0x2EFF],  # CJK Radicals Supplement (CJK Unified Ideographs)
    [0x2F00, 0x2FDF],  # Kangxi Radicals (CJK Unified Ideographs)
    [0x2FF0, 0x2FFF],  # Ideographic Description Characters (CJK Unified Ideographs)
    [0x3400, 0x4DBF],  # CJK Unified Ideographs Extension A (CJK Unified Ideographs)
    [0x20000, 0x2A6DF],  # CJK Unified Ideographs Extension B (CJK Unified Ideographs)
    [0x3190, 0x319F],  # Kanbun (CJK Unified Ideographs)
    [0x31C0, 0x31EF],  # CJK Strokes
    [0xF900, 0xFAFF],  # CJK Compatibility Ideographs (CJK Strokes)
    [0x2F800, 0x2FA1F],  # CJK Compatibility Ideographs Supplement (CJK Strokes)
    [0xA000, 0xA48F],  # Yi Syllables
    [0xA490, 0xA4CF],  # Yi Radicals
]

# =================================
# Utility functions
# =================================


def get_corrected_range_bit(n):
    """Returns a 32 bit index value for each of the four uint32 that define the OS/2.ulUnicodeRange 1 through 4."""
    if n < 32:
        return n
    elif n in range(32, 63):
        return (n - 32)
    elif n in range(64, 95):
        return (n - 64)
    elif n in range(96, 127):
        return (n - 96)
    else:
        return None


def is_kth_bit_set(j, k):
    if j & (1 << k):
        return True
    else:
        return False


# =================================
# Conditions
# =================================


@condition
def is_cjk_font(ttFont):
    """Test font object to confirm that it meets our definition of a CJK font file.
    The definition is met if any of the following conditions are True:
       1. The font has a CJK code page bit set in the OS/2 table
       2. The font has a CJK Unicode range bit set in the OS/2 table
       3. The font has any CJK Unicode code points defined in the cmap table"""
    os2 = ttFont["OS/2"]

    # OS/2 code page checks
    os2_cpr1 = os2.ulCodePageRange1
    for _, bit in CJK_CODEPAGE_BITS.items():
        if is_kth_bit_set(os2_cpr1, bit):
            return True

    # OS/2 Unicode range checks
    range1 = os2.ulUnicodeRange1
    range2 = os2.ulUnicodeRange2
    range3 = os2.ulUnicodeRange3
    for _, bit in CJK_UNICODE_RANGE_BITS.items():
        if bit < 32:
            # check range 1 for bits 0 - 31
            if is_kth_bit_set(range1, bit):
                return True
        elif bit in range(32, 63):
            # check range 2 for bits 32 - 63
            if is_kth_bit_set(range2, get_corrected_range_bit(bit)):
                return True
        elif bit in range(64, 95):
            # check range 3 for bits 64 - 95
            if is_kth_bit_set(range3, get_corrected_range_bit(bit)):
                return True

    # defined CJK Unicode code point in cmap table checks
    cmap = ttFont.getBestCmap()
    for unicode_range in UNICODE_RANGES:
        for x in range(unicode_range[0], unicode_range[1]):
            if int(x) in cmap:
                return True

    # default, return False if the above checks did not identify a CJK font
    return False

# =================================
# Checks
# =================================


@check(
    id='com.google.fonts/check/cjk/example',
    conditions=["is_cjk_font"]
)
def com_google_fonts_check_cjk_example(ttFont):
    """ Example check docstring. """
    failed = False
    if "some condition":
        failed = True
        foo = 123
        yield FAIL, Message("why-did-it-fail-keyword",
                            (f"Something is bad because of {foo}."
                            " Please considering fixing by doing so and so."))
    elif "a warning":
        failed = True
        yield WARN, (f"Beware of so and so!")

    elif "informative message":
        yield INFO, (f"This is an INFO msg...")

    if not failed:
        yield PASS, ("All looks great!")


profile.auto_register(globals())
profile.test_expected_checks(CJK_PROFILE_CHECKS, exclusive=True)
