from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS
from fontbakery.message import Message

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


def _check_call_depth(top_dict, private_dict, fd_index=0):
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
    failed = False
    for glyph_name in char_list:
        t2_char_string, fd_select_index = char_strings.getItemAndSelector(
            glyph_name)
        if fd_select_index is not None and fd_select_index != fd_index:
            continue
        try:
            t2_char_string.decompile()
        except RecursionError:
            yield FAIL,\
                  Message("recursion-error",
                          f'Recursion error while decompiling'
                          f' glyph "{glyph_name}".')
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
            yield FAIL,\
                  Message("max-depth",
                          f'Subroutine call depth exceeded'
                          f' maximum of 10 for glyph "{glyph_name}".')
            failed = True
    return failed


@check(
  id = 'com.adobe.fonts/check/cff_call_depth',
  conditions = ['is_cff'],
  rationale = """
    Per "The Type 2 Charstring Format, Technical Note #5177", the "Subr nesting, stack limit" is 10.
  """
)
def com_adobe_fonts_check_cff_call_depth(ttFont):
    """Is the CFF subr/gsubr call depth > 10?"""
    any_failures = False
    cff = ttFont['CFF '].cff

    for top_dict in cff.topDictIndex:
        if hasattr(top_dict, 'FDArray'):
            for fd_index, font_dict in enumerate(top_dict.FDArray):
                if hasattr(font_dict, 'Private'):
                    private_dict = font_dict.Private
                else:
                    private_dict = None
                failed = yield from \
                    _check_call_depth(top_dict, private_dict, fd_index)
                any_failures = any_failures or failed
        else:
            if hasattr(top_dict, 'Private'):
                private_dict = top_dict.Private
            else:
                private_dict = None
            failed = yield from _check_call_depth(top_dict, private_dict)
            any_failures = any_failures or failed

    if not any_failures:
        yield PASS, 'Maximum call depth not exceeded.'


@check(
  id = 'com.adobe.fonts/check/cff2_call_depth',
  conditions = ['is_cff2'],
  rationale = """
    Per "The CFF2 CharString Format", the "Subr nesting, stack limit" is 10.
  """
)
def com_adobe_fonts_check_cff2_call_depth(ttFont):
    """Is the CFF2 subr/gsubr call depth > 10?"""
    any_failures = False
    cff = ttFont['CFF2'].cff

    for top_dict in cff.topDictIndex:
        for fd_index, font_dict in enumerate(top_dict.FDArray):
            if hasattr(font_dict, 'Private'):
                private_dict = font_dict.Private
            else:
                private_dict = None
            failed = yield from \
                _check_call_depth(top_dict, private_dict, fd_index)
            any_failures = any_failures or failed

    if not any_failures:
        yield PASS, 'Maximum call depth not exceeded.'
