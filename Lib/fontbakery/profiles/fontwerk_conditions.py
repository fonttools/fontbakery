
from fontTools.misc.fixedTools import fixedToFloat

general = {
    "embedding level": "Print and Preview",
    "vendor id": 'WERK',
    "name table": {
        # name table platform: (3,1,1033,XX)
        0: r'Copyright (c) [0-9]{4}(\-[0-9]{4})? Fontwerk GmbH. All rights reserved.',  # name ID 0: Copyright
        1: r'^[a-zA-Z0-9 ]{1,31}',  # name ID 1: Family Name min 1 max 31 characters
        2: r'\b(?:Regular|Bold Italic|Bold|Italic)\b',  # name ID 2: Subfamily Name, must be 'Regular', 'Bold', 'Italic' or 'Bold Italic'
        3: r'^[a-zA-Z0-9-]{1,31}',  # no spaces, but dash allowed
        6: r'^[a-zA-Z0-9-]{1,28}',  # no spaces, but dash allowed
        5: r"Version [0-9]{1}.[0-9]{2}",  # name ID 5: Version String, [[VERSION-NUMBER]] max two dezimal eg. 1.01 NOT 1.001
        7: r".* is a trademark of Fontwerk GmbH",  # name ID 7: Trademark
        8: 'Fontwerk',  # name ID 8: Manufacturer
        9: r'.*',  # name ID 9: Designer; name of the designer of the typeface.
        10: r"Original Fontwerk font\.[\r\n]+Revision Information:[\r\n]+1.00 Release.*",  # eg. 1.01 Bug fix spacing, update fontinfo, improve kerning   # name ID 10: Description + Versionierung + Marketing-Text, sobald vorhanden, spätestens ab V 1.01
        11: "https://fontwerk.com",  # name ID 11: URL Vendor
        12: r"https:\/\/fontwerk\.com\/designers\/.*-.*",  # name ID 12: URL Designer
        13: r"This Font Software is the property of Fontwerk GmbH and its use by you is covered under the terms of an End-User License Agreement \(EULA\)\. Unless you have entered into a specific license agreement granting you additional rights, your use of this Font Software is limited by the terms of the actual license agreement you have entered into with Fontwerk\. If you have any questions concerning your rights you should review the EULA you received with the software or contact Fontwerk\. A copy of the EULA for this Font Software can be found on https:\/\/fontwerk\.com\/licensing\.",  # name ID 13: License Description
        14: "https://fontwerk.com/licensing",  # name ID 14: URL License
    },

}

trial = {
    # only if different to general
    "name table": {
        10: "Original Fontwerk font. Trial version only. Please license the regular fonts in order to access the complete character set and functionality, and you are covered by the proper usage rights.",  # name ID 10: Description
        13: "TRIAL LICENSE: This Font Software is the property of Fontwerk GmbH and its use by you is covered under the terms of an End-User License Agreement (EULA) for Trial Fonts. Unless you have entered into a license agreement granting you additional rights, your use of this Font Software is limited to testing purposes by the terms of the actual license agreement you have entered into with Fontwerk. If you have any questions concerning your rights you should review the EULA you received with the software or contact Fontwerk. A copy of the Trial Font EULA for this Font Software can be found on https://fontwerk.com/licensing.",  # name ID 13: License Description
    },

}

variable = {
    "hinting": False,
}

ttf = {
    "kerning": {
        "GPOS": True,
        "kern": True,
    },
    "post table format": 2,
    "hinting": True,
}

cff = {
    "hinting": True,
    "kerning": {
        "GPOS": True,
        "kern": False,
    },
    "post table format": 3,
},

webfont = {
    "post table format": 3,
    "name table": {
        1: "",  # name ID 1: Family Name must be empty, so it cannot be installed
    },
}

_WEIGHT_VALUES = {
    'Hairline': {"usWeightClass": 50, "fvar": 50.0},
    'Thin': {"usWeightClass": 100, "fvar": 100.0},
    'ExtraLight': {"usWeightClass": 200, "fvar": 200.0},
    'Light': {"usWeightClass": 300, "fvar": 300.0},
    'SemiLight': {"usWeightClass": 350, "fvar": 350.0},
    'Regular': {"usWeightClass": 300, "fvar": 400.0},
    'Medium': {"usWeightClass": 500, "fvar": 500.0},
    'SemiBold': {"usWeightClass": 600, "fvar": 600.0},
    'Bold': {"usWeightClass": 700, "fvar": 700.0},
    'ExtraBold': {"usWeightClass": 800, "fvar": 800.0},
    'Black': {"usWeightClass": 900, "fvar": 900.0},
    'ExtraBlack': {"usWeightClass": 1000, "fvar": 1000.0}, # alternative name: 'Heavy'
}

_WIDTH_VALUES = {
    'ExtraCompressed': {"usWidthClass": 1, "fvar": 50.0},
    'Compressed': {"usWidthClass": 2, "fvar": 62.5},
    'Condensed': {"usWidthClass": 3, "fvar": 75.0},
    'SemiCondensed': {"usWidthClass": 4, "fvar": 87.5}, # alternative name: 'Narrow'
    'Normal': {"usWidthClass": 5, "fvar": 100.0},
    'SemiExtended': {"usWidthClass": 6, "fvar": 112.5},
    'Extended': {"usWidthClass": 7, "fvar": 125.0},
    'Wide': {"usWidthClass": 8, "fvar": 150.0},
    'ExtraWide': {"usWidthClass": 9, "fvar": 200.0},
}

_OPTICAL_SIZE_VALUES = {
    'Micro': {"min": fixedToFloat(-0x80000000, 16), "default": 6.0, "max": 8.0},
    'Text': {"min": 8.0, "default": 12.0, "max": 16.0},
    'Headline': {"min": 16.0, "default": 20.0, "max": 22.0},
    'Poster': {"min": 22.0, "default": 28.0, "max": fixedToFloat(0x7FFFFFFF, 16)},
}

# item 0: preferred name
# item 1: preferred abbreviation
# item 2: smallest abbreviation
# all other: not preferred, but possible
_WEIGHT_NAMES = {
    'Hairline': ['Hairline', 'Hair', 'Hr'],
    'Thin': ['Thin', 'Thn',  'Th'],
    'ExtraLight': ['ExtraLight', 'XLight', 'XLt',
                   'ExtraLight', 'Extra Light', 'Extra-Light',
                   'ExtLight', 'Ext Light', 'Ext-Light',
                   'ExLight', 'Ex Light', 'Ex-Light',
                   'XLight', 'X Light', 'X-Light',

                   'ExtraLt', 'Extra Lt', 'Extra-Lt',
                   'ExtLt', 'Ext Lt', 'Ext-Lt',
                   'ExLt', 'Ex Lt', 'Ex-Lt',
                   'XLt', 'X Lt', 'X-Lt',
                   ],
    'SemiLight': ['SemiLight', 'SemiLt', 'SLt',
                  'SemiLight', 'Semi Light', 'Semi-Light',
                  'SmLight', 'Sm Light', 'Sm-Light',
                  'SLight', 'S Light', 'S-Light',

                  'SemiLt', 'Semi Lt', 'Semi-Lt',
                  'SmLt', 'Sm Lt', 'Sm-Lt',
                  'SLt', 'S Lt', 'S-Lt',
                  ],
    'Light': ['Light', 'Lt', 'Lt'],
    'Regular': ['Regular', 'Reg', 'Rg',
                ''],
    'Medium': ['Medium', 'Med', 'Md',
               'Medi'],
    'SemiBold': ['SemiBold', 'SemiBd', 'SBld',
                 'SemiBold', 'Semi Bold', 'Semi-Bold',
                 'SmBold', 'Sm Bold', 'Sm-Bold',
                 'SBold', 'S Bold', 'S-Bold',

                 'SemiBld', 'Semi Bld', 'Semi-Bld',
                 'SmBld', 'Sm Bld', 'Sm-Bld',
                 'SBld', 'S Bld', 'S-Bld',

                 'SemiBd', 'Semi Bd', 'Semi-Bd',
                 'SmBd', 'Sm Bd', 'Sm-Bd',
                 'SBd', 'S Bd', 'S-Bd'],
    'Bold': ['Bold', 'Bld', 'Bd'],
    'ExtraBold': ['ExtraBold', 'XBold', 'XBld',
                  'ExtraBold', 'Extra Bold', 'Extra-Bold',
                  'ExtBold', 'Ext Bold', 'Ext-Bold',
                  'ExBold', 'Ex Bold', 'Ex-Bold',
                  'XBold', 'X Bold', 'X-Bold',

                  'ExtraBld', 'Extra Bld', 'Extra-Bld',
                  'ExtBld', 'Ext Bld', 'Ext-Bld',
                  'ExBld', 'Ex Bld', 'Ex-Bld',
                  'XBld', 'X Bld', 'X-Bld',

                  'ExtraBd', 'Extra Bd', 'Extra-Bd',
                  'ExtBd', 'Ext Bd', 'Ext-Bd',
                  'ExBd', 'Ex Bd', 'Ex-Bd',
                  'XBd', 'X Bd', 'X-Bd'],
    'Black': ['Black', 'Blk', 'Bk',
              'Bla', 'Bl'],
    'ExtraBlack': ['ExtraBlack', 'XBlack', 'XBlk',
                   'ExtraBlack', 'Extra Black', 'Extra-Black',
                   'ExtBlack', 'Ext Black', 'Ext-Black',
                   'ExBlack', 'Ex Black', 'Ex-Black',
                   'XBlack', 'X Black', 'X-Black',

                   'ExtraBlk', 'Extra Blk', 'Extra-Blk',
                   'ExBlk', 'Ex Blk', 'Ex-Blk',
                   'XBlk', 'X Blk', 'X-Blk',

                   'ExtraBla', 'Extra Bla', 'Extra-Bla',
                   'ExBla', 'Ex Bla', 'Ex-Bla',
                   'XBla', 'X Bla', 'X-Bla',

                   'ExtraBk', 'Extra Bk', 'Extra-Bk',
                   'ExBk', 'Ex Bk', 'Ex-Bk',
                   'XBk', 'X Bk', 'X-Bk',

                   'ExtraBl', 'Extra Bl', 'Extra-Bl',
                   'ExBl', 'Ex Bl', 'Ex-Bl',
                   'XBl', 'X Bl', 'X-Bl'],
}

_WIDTH_NAMES = {
    'ExtraCompressed': ['ExtraCompressed', 'XCompressed', 'XComp',
                        'ExtraCompressed', 'Extra Compressed', 'Extra-Compressed',
                        'ExtraComp', 'Extra Comp', 'Extra-Comp',
                        'ExtraCmp', 'Extra Cmp', 'Extra-Cmp',
                        'ExtraCp', 'Extra Cp', 'Extra-Cp',

                        'ExtCompressed', 'Ext Compressed', 'Ext-Compressed',
                        'ExtComp', 'Ext Comp', 'Ext-Comp',
                        'ExtCmp', 'Ext Cmp', 'Ext-Cmp',
                        'ExtCp', 'Ext Cp', 'Ext-Cp',

                        'ExCompressed', 'Ex Compressed', 'Ex-Compressed',
                        'ExComp', 'Ex Comp', 'Ex-Comp',
                        'ExCmp', 'Ex Cmp', 'Ex-Cmp',
                        'ExCp', 'Ex Cp', 'Ex-Cp',

                        'XCompressed', 'X Compressed', 'X-Compressed',
                        'XComp', 'X Comp', 'X-Comp',
                        'XCmp', 'X Cmp', 'X-Cmp',
                        'XCp', 'X Cp', 'X-Cp',
                        ],
    'Compressed': ['Compressed', 'Comp', 'Cmp',
                   'Cp'],
    'Condensed': ['Condensed', 'Cond', 'Cnd',
                  'Cn', 'Cd'],
    'SemiCondensed': ['SemiCondensed', 'SemiCond', 'SemiCnd',
                      'SemiCondensed', 'Semi Condensed', 'Semi-Condensed',
                      'SemiCond', 'Semi Cond', 'Semi-Cond',
                      'SemiCnd', 'Semi Cnd', 'Semi-Cnd',
                      'SemiCd', 'Semi Cd', 'Semi-Cd',

                      'SmCondensed', 'Sm Condensed', 'Sm-Condensed',
                      'SmCond', 'Sm Cond', 'Sm-Cond',
                      'SmCnd', 'Sm Cnd', 'Sm-Cnd',
                      'SmCd', 'Sm Cd', 'Sm-Cd',

                      'SCondensed', 'S Condensed', 'S-Condensed',
                      'SCond', 'S Cond', 'S-Cond',
                      'SCnd', 'S Cnd', 'S-Cnd',
                      'SCd', 'S Cd', 'S-Cd',
                      ],
    'Normal': ['Normal', 'Norm', ''],
    'SemiExtended': ['SemiExtended', 'Semi-Extended', 'Semi Extended',
                     'SemiExtd', 'Semi-Extd', 'Semi Extd',
                     'SemiExt', 'Semi-Ext', 'Semi Ext',

                     'SmExtended', 'Sm-Extended', 'Sm Extended',
                     'SmExtd', 'Sm-Extd', 'Sm Extd',
                     'SmExt', 'Sm-Ext', 'Sm Ext',

                     'SExtended', 'S-Extended', 'S Extended',
                     'SExtd', 'S-Extd', 'S Extd',
                     'SExt', 'S-Ext', 'S Ext',
                     ],
    'Extended': ['Extended', 'Extd', 'Ext'],
    'Wide': ['Wide', 'Wid', 'Wd'],
    'ExtraWide': ['ExtraWide', 'XWide', 'XWd',
                  'ExtraWide', 'Extra-Wide', 'Extra Wide',
                  'ExtWide', 'Ext-Wide', 'Ext Wide',
                  'ExWide', 'Ex-Wide', 'Ex Wide',
                  'XWide', 'X-Wide', 'X Wide',

                  'ExtraWid', 'Extra-Wid', 'Extra Wid',
                  'ExtWid', 'Ext-Wid', 'Ext Wid',
                  'ExWid', 'Ex-Wid', 'Ex Wid',
                  'XWid', 'X-Wid', 'X Wid',

                  'ExtraWd', 'Extra-Wd', 'Extra Wd',
                  'ExtWd', 'Ext-Wd', 'Ext Wd',
                  'ExWd', 'Ex-Wd', 'Ex Wd',
                  'XWd', 'X-Wd', 'X Wd',
                  ],
}

_AXIS_TAGS = {
    # https://docs.microsoft.com/en-us/typography/opentype/spec/dvaraxisreg#registered-axis-tags
    # registered: must be lowercase letters.
    'ital' : 'Italic',
    'opsz' : 'Optical size',
    'slnt' : 'Slant',
    'wdth' : 'Width',
    'wght' : 'Weight',
    # unregistered: must be uppercase letters.
    'CONT': 'Contrast',
}
