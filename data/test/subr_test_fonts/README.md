# test fonts for testing CFF/CFF2 subroutine (subr/gsubr) call depth checking

`subr_test_font_infinite_recursion.otf` is a CFF font which includes glyphs that call into private & global subroutines to different call depths, and includes a glyph with infinite recursion in its calls:

```
.notdef -- max depth: 0
space -- max depth: 0
A -- max depth: 2
B -- max depth: 9
C -- max depth: 10
FAIL: D -- max depth: 11
FAIL: E -- max depth: 12
FAIL: recursion error while decompiling glyph F
```

`var_subr_test_font_infinite_recursion.otf` is a CFF2 font with the same properties as `subr_test_font_infinite_recursion.otf`.

I (cjchapman) created these fonts by first subsetting `SourceCodePro-Regular.otf` and `SourceCodeVariable-Roman.otf`, e.g.:

```
pyftsubset SourceCodePro-Regular.otf —gids=0-7 —drop-tables+=GSUB,GPOS,GDEF —output-file=original_subset.otf
pyftsubset SourceCodeVariable-Roman.otf  --gids=0-7 --drop-tables+=GSUB,GPOS,GDEF --output-file=var_original_subset.otf
```
then I used `ttx` to disassemble the `CFF` and `CFF2` fonts into XML, then I hand-edited in some private & global subroutines to create various call depths, then I used `ttx` to compile the hand-edited XML back into the fonts, and finally I used a hex editor to hack one of the global subroutines to call itself (for infinite recursion).
