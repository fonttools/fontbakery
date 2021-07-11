from fontbakery.callable import check, condition
from fontbakery.status import FAIL, PASS, WARN
from fontbakery.message import Message

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import

profile_imports = [
    ('.shared_conditions', ('is_cff', 'is_cff2'))
]

class CFFAnalysis:
    def __init__(self):
        self.glyphs_dotsection = []
        self.glyphs_endchar_seac = []
        self.glyphs_exceed_max = []
        self.glyphs_recursion_errors = []

def _get_subr_bias(count):
    if count < 1240:
        bias = 107
    elif count < 33900:
        bias = 1131
    else:
        bias = 32768
    return bias


def _traverse_subr_call_tree(info, program, depth):
    global_subrs = info['global_subrs']
    subrs = info['subrs']
    gsubr_bias = info['gsubr_bias']
    subr_bias = info['subr_bias']

    if depth > info['max_depth']:
        info['max_depth'] = depth

    # once we exceed the max depth we can stop going deeper
    if depth > 10:
        return

    if len(program) >=5 and program[-1] == 'endchar' and all([isinstance(a, int) for a in program[-5:-1]]):
        info['saw_endchar_seac'] = True
    if 'ignore' in program:  # decompiler expresses 'dotsection' as 'ignore'
        info['saw_dotsection'] = True

    while program:
        x = program.pop()
        if x == 'callgsubr':
            y = int(program.pop()) + gsubr_bias
            sub_program = global_subrs[y].program.copy()
            _traverse_subr_call_tree(info, sub_program, depth + 1)
        elif x == 'callsubr':
            y = int(program.pop()) + subr_bias
            sub_program = subrs[y].program.copy()
            _traverse_subr_call_tree(info, sub_program, depth + 1)


def _analyze_cff(analysis, top_dict, private_dict, fd_index=0):
    char_strings = top_dict.CharStrings
    global_subrs = top_dict.GlobalSubrs
    gsubr_bias = _get_subr_bias(len(global_subrs))

    if private_dict is not None and hasattr(private_dict, 'Subrs'):
        subrs = private_dict.Subrs
        subr_bias = _get_subr_bias(len(subrs))
    else:
        subrs = None
        subr_bias = None

    char_list = char_strings.keys()

    for glyph_name in char_list:
        t2_char_string, fd_select_index = char_strings.getItemAndSelector(
            glyph_name)
        if fd_select_index is not None and fd_select_index != fd_index:
            continue
        try:
            t2_char_string.decompile()
        except RecursionError:
            analysis.glyphs_recursion_errors.append(glyph_name)
            continue
        info = dict()
        info['subrs'] = subrs
        info['global_subrs'] = global_subrs
        info['gsubr_bias'] = gsubr_bias
        info['subr_bias'] = subr_bias
        info['max_depth'] = 0
        depth = 0
        program = t2_char_string.program.copy()
        _traverse_subr_call_tree(info, program, depth)
        max_depth = info['max_depth']

        if max_depth > 10:
            analysis.glyphs_exceed_max.append(glyph_name)
        if info.get('saw_endchar_seac'):
            analysis.glyphs_endchar_seac.append(glyph_name)
        if info.get('saw_dotsection'):
            analysis.glyphs_dotsection.append(glyph_name)

@condition
def cff_analysis(ttFont):

    analysis = CFFAnalysis()

    if 'CFF ' in ttFont:
        cff = ttFont['CFF '].cff

        for top_dict in cff.topDictIndex:
            if hasattr(top_dict, 'FDArray'):
                for fd_index, font_dict in enumerate(top_dict.FDArray):
                    if hasattr(font_dict, 'Private'):
                        private_dict = font_dict.Private
                    else:
                        private_dict = None
                    _analyze_cff(analysis, top_dict, private_dict, fd_index)
            else:
                if hasattr(top_dict, 'Private'):
                    private_dict = top_dict.Private
                else:
                    private_dict = None
                _analyze_cff(analysis, top_dict, private_dict)

    elif 'CFF2' in ttFont:
        cff = ttFont['CFF2'].cff

        for top_dict in cff.topDictIndex:
            for fd_index, font_dict in enumerate(top_dict.FDArray):
                if hasattr(font_dict, 'Private'):
                    private_dict = font_dict.Private
                else:
                    private_dict = None
                _analyze_cff(analysis, top_dict, private_dict, fd_index)

    return analysis

@check(
    id = 'com.adobe.fonts/check/cff_call_depth',
    conditions = ['ttFont',
                  'is_cff',
                  'cff_analysis'],
    rationale = """
        Per "The Type 2 Charstring Format, Technical Note #5177", the "Subr nesting, stack limit" is 10.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/2425'
)
def com_adobe_fonts_check_cff_call_depth(cff_analysis):
    """Is the CFF subr/gsubr call depth > 10?"""

    any_failures = False

    if cff_analysis.glyphs_exceed_max or cff_analysis.glyphs_recursion_errors:
        any_failures = True
        for gn in cff_analysis.glyphs_exceed_max:
            yield FAIL, \
                  Message('max-depth',
                          f'Subroutine call depth exceeded maximum of 10 for glyph "{gn}".')
        for gn in cff_analysis.glyphs_recursion_errors:
            yield FAIL, \
                  Message('recursion-error',
                          f'Recursion error while decompiling glyph "{gn}".')

    if not any_failures:
        yield PASS, 'Maximum call depth not exceeded.'


@check(
    id = 'com.adobe.fonts/check/cff2_call_depth',
    conditions = ['ttFont', 'is_cff2', 'cff_analysis'],
    rationale = """
        Per "The CFF2 CharString Format", the "Subr nesting, stack limit" is 10.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/2425'
)
def com_adobe_fonts_check_cff2_call_depth(cff_analysis):
    """Is the CFF2 subr/gsubr call depth > 10?"""

    any_failures = False

    if cff_analysis.glyphs_exceed_max or cff_analysis.glyphs_recursion_errors:
        any_failures = True
        for gn in cff_analysis.glyphs_exceed_max:
            yield FAIL, \
                  Message('max-depth',
                          f'Subroutine call depth exceeded maximum of 10 for glyph "{gn}".')
        for gn in cff_analysis.glyphs_recursion_errors:
            yield FAIL, \
                  Message('recursion-error',
                          f'Recursion error while decompiling glyph "{gn}".')

    if not any_failures:
        yield PASS, 'Maximum call depth not exceeded.'


@check(
    id = 'com.adobe.fonts/check/cff_deprecated_operators',
    conditions = ['ttFont',
                  'is_cff',
                  'cff_analysis'],
    rationale = """
        The 'dotsection' operator and the use of 'endchar' to build accented characters from the Adobe Standard Encoding Character Set ("seac") are deprecated in CFF. Adobe recommends repairing any fonts that use these, especially endchar-as-seac, because a rendering issue was discovered in Microsoft Word with a font that makes use of this operation. The check treats that useage as a FAIL. There are no known ill effects of using dotsection, so that check is a WARN.
    """,
    proposal = 'https://github.com/googlefonts/fontbakery/pull/3033'
)
def com_adobe_fonts_check_cff_deprecated_operators(cff_analysis):
    """Does the font use deprecated CFF operators or operations?"""
    any_failures = False

    if cff_analysis.glyphs_dotsection or cff_analysis.glyphs_endchar_seac:
        any_failures = True
        for gn in cff_analysis.glyphs_dotsection:
            yield WARN, \
                  Message('deprecated-operator-dotsection',
                          f'Glyph "{gn}" uses deprecated "dotsection" operator.')
        for gn in cff_analysis.glyphs_endchar_seac:
            yield FAIL, \
                  Message('deprecated-operation-endchar-seac',
                          f'Glyph "{gn}" has deprecated use of "endchar" operator to build accented characters (seac).')

    if not any_failures:
        yield PASS, 'No deprecated CFF operators used.'
