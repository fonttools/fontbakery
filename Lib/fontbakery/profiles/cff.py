from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS

# used to inform get_module_profile whether and how to create a profile
from fontbakery.fonts_profile import profile_factory # NOQA pylint: disable=unused-import


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


@check(
    id='com.adobe.fonts/check/cff_call_depth',
    conditions=['is_cff'],
    rationale="""Per "The Type 2 Charstring Format, Technical Note #5177",
    the "Subr nesting, stack limit" is 10."""
)
def com_adobe_fonts_check_cff_call_depth(ttFont):
    """Is the CFF subr/gsubr call depth > 10?"""
    failed = False
    cff = ttFont['CFF '].cff

    for top_dict in cff.topDictIndex:
        char_strings = top_dict.CharStrings

        global_subrs = top_dict.GlobalSubrs
        gsubr_bias = _get_subr_bias(len(global_subrs))

        subrs = top_dict.Private.Subrs
        subr_bias = _get_subr_bias(len(subrs))

        char_list = char_strings.keys()
        for key in char_list:
            t2_char_string = char_strings[key]
            try:
                t2_char_string.decompile()
            except RecursionError:
                yield FAIL, "Recursion error while " \
                            "decompiling glyph '{}'.".format(key)
                failed = True
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
                yield FAIL, "Subroutine call depth exceeded " \
                            "maximum of 10 for glyph '{}'.".format(key)
                failed = True
    if not failed:
        yield PASS, 'Maximum call depth not exceeded.'


@check(
    id='com.adobe.fonts/check/cff2_call_depth',
    conditions=['is_cff2'],
    rationale="""Per "The CFF2 CharString Format",
    the "Subr nesting, stack limit" is 10."""
)
def com_adobe_fonts_check_cff2_call_depth(ttFont):
    """Is the CFF2 subr/gsubr call depth > 10?"""
    failed = False
    cff = ttFont['CFF2'].cff

    for top_dict in cff.topDictIndex:
        char_strings = top_dict.CharStrings

        global_subrs = top_dict.GlobalSubrs
        gsubr_bias = _get_subr_bias(len(global_subrs))

        for font_dict in top_dict.FDArray:
            subrs = font_dict.Private.Subrs
            subr_bias = _get_subr_bias(len(subrs))

            char_list = char_strings.keys()
            for key in char_list:
                t2_char_string = char_strings[key]
                try:
                    t2_char_string.decompile()
                except RecursionError:
                    yield FAIL, "Recursion error while " \
                                "decompiling glyph '{}'.".format(key)
                    failed = True
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
                    yield FAIL, "Subroutine call depth exceeded " \
                                "maximum of 10 for glyph '{}'.".format(key)
                    failed = True
    if not failed:
        yield PASS, 'Maximum call depth not exceeded.'
