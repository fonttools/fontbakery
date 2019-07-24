from fontTools import ttLib
import sys

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

def CheckOS2uRanges(font):
    OS2 = font['OS/2']
    range1 = bin(OS2.ulUnicodeRange1)[2:].zfill(32)
    range2 = bin(OS2.ulUnicodeRange2)[2:].zfill(32)
    range3 = bin(OS2.ulUnicodeRange3)[2:].zfill(32)
    range4 = bin(OS2.ulUnicodeRange4)[2:].zfill(32)
    allRanges = range1+range2+range3+range4
    print("UnicodeRanges:", allRanges)
    for k, v in unicodeRanges.items():
        print(v, ':', int(allRanges[k])==1)

if __name__ == '__main__':
    if len(sys.argv):
        inputFont = ttLib.TTFont(sys.argv[1])
        CheckOS2uRanges(inputFont)
