import os
import sys

from fontTools.ttLib import TTFont


codepage_dict = {
    "jp": 17,
    "sc": 18,
    "krw": 19,
    "tc": 20,
    "krj": 21
}

unicodeRanges = {
    28: 'Hangul Jamo',
    48: 'CJK Symbols And Punctuation',
    49: 'Hiragana',
    50: 'Katakana',
    51: 'Bopomofo',
    52: 'Hangul Compatibility Jamo',
    54: 'Enclosed CJK Letters And Months',
    55: 'CJK Compatibility',
    56: 'Hangul Syllables',
    59: 'CJK Unified Ideographs',
    61: 'CJK Strokes',
    83: 'Yi Syllables'
}


def is_kth_bit_set(j, k):
    if j & (1 << k): 
        return True
    else: 
        return False


def check_os2_unicode_ranges(font):
    OS2 = font['OS/2']
    range1 = bin(OS2.ulUnicodeRange1)[2:].zfill(32)
    range2 = bin(OS2.ulUnicodeRange2)[2:].zfill(32)
    range3 = bin(OS2.ulUnicodeRange3)[2:].zfill(32)
    range4 = bin(OS2.ulUnicodeRange4)[2:].zfill(32)
    allRanges = range1+range2+range3+range4
    # print("UnicodeRanges:", allRanges)
    for k, v in unicodeRanges.items():
        print("{} (bit {}): {}".format(v, k, int(allRanges[k])==1))


def main(argv):
    for font in argv:
        # tt = TTFont(font, fontNumber=0)  # this is how TTC is instantiated by font in the collection
        tt = TTFont(font)
        cpr_dict = {}
        os2 = tt["OS/2"]
        os2_cpr1 = os2.ulCodePageRange1
        os2_cpr2 = os2.ulCodePageRange2

        cpr_dict["jp"] = is_kth_bit_set(os2_cpr1, codepage_dict["jp"])
        cpr_dict["sc"] = is_kth_bit_set(os2_cpr1, codepage_dict["sc"])
        cpr_dict["krw"] = is_kth_bit_set(os2_cpr1, codepage_dict["krw"])
        cpr_dict["tc"] = is_kth_bit_set(os2_cpr1, codepage_dict["tc"])
        cpr_dict["krj"] = is_kth_bit_set(os2_cpr1, codepage_dict["krj"])


        print("{}{}".format(font, os.linesep))

        print(">>> Unicode Code Pages:{}".format(os.linesep))
        print("JP (bit 17): {}".format(cpr_dict["jp"]))
        print("SC (bit 18): {}".format(cpr_dict["sc"]))
        print("KR-W (bit 19): {}".format(cpr_dict["krw"]))
        print("TC (bit 20): {}".format(cpr_dict["tc"]))
        print("KR-J (bit 21): {}".format(cpr_dict["krj"]))
        print(os.linesep)

        print(">>> Unicode Ranges:{}".format(os.linesep))
        check_os2_unicode_ranges(tt)

        print(os.linesep)
        print("-" * 20)
        print(os.linesep)


if __name__ == '__main__':
    main(sys.argv[1:])
