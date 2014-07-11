# Fontcrunch
*5 Jul 2014*
Raph Levien, Google

This is a tool for TrueType font spline optimization - a "simplify" command.

It tries to create a visual match for the spline using the smallest number of TrueType points. 

It is notable for counting on-curve points interpolated between two off-curve points as "free," making useful filesize savings.

It depends on fonttools, and has some legacy dependencies on [spiro-0.01](http://www.levien.com/spiro/spiro-0.01.tar.gz)

This code is available under the Apache v2 license. Spiro code is GNU GPL v2 or later, and Spiro curves are subject to a US patent.

1. `python fontcrunch.py gen yourfont.ttf`

This creates 256 directories named 00 .. ff, and populates them with lots of files with .bz extension.
Each of these is a nontrivial segment of quad beziers cut from the font, stored as a `x0 y0 x1 y1 x2 y2` line per bezier.
Lines are represented with `(x1, y1)` at the midpoint of the two endpoints.

2. `make -j16 # or whatever level of parallelism makes sense on your computer`

This runs the optimizer on each of the .bz files, producing a .bzopt.
You can control the level of precision by editing "penalty" in the code (should of course be a parameter).
On a fast computer, it should go through about 5 glyphs a second, depending on complexity.

3. `python fontcrunch.py pack yourfont.ttf > /tmp/outlines.ps newfont.ttf`

This regenerates a new TrueType font. You can look at the outlines to check the quality of the result.
