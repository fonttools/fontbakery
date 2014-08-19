# Fontcrunch

By Raph Levien, Google

This is a tool for TrueType font spline optimization - a "simplify" command.
It tries to create a visual match for the spline using the smallest number of TrueType points. 
It is notable for counting on-curve points interpolated between two off-curve points as "free," making useful filesize savings.

It depends on fonttools, and has some legacy dependencies on [spiro-0.01](http://www.levien.com/spiro/spiro-0.01.tar.gz)
This code is available under the Apache v2 license. Spiro code is GNU GPL v2 or later, and Spiro curves are subject to a US patent.

## Usage

Create 256 directories named 00 .. ff, and populate them with lots of files with .bz extension.
Each of these is a nontrivial segment of quad beziers cut from the font, stored as a `x0 y0 x1 y1 x2 y2` line per bezier.
Lines are represented with `(x1, y1)` at the midpoint of the two endpoints.

`python fontcrunch.py gen yourfont.ttf`

Runs the optimizer on each of the .bz files, producing a .bzopt.
You can control the level of precision by editing "penalty" in the code (should of course be a parameter).
On a fast computer, it should go through about 5 glyphs a second, depending on complexity.

`make -j16 # or whatever level of parallelism makes sense on your computer`

Regenerate a new TrueType font. You can look at the outlines to check the quality of the result.

`python fontcrunch.py pack yourfont.ttf > /tmp/outlines.ps newfont.ttf`

## How It Works

The basic ideas of this are fairly similar to Chapter 9 of [my thesis (PDF)](http://levien.com/phd/thesis.pdf). The main differences are: quadratic instead of cubic beziers; grid-quantized coordinates rather than float; and the off-curve point optimization (see below.)

The C++ code expects a curve segment, made of multiple quad beziers, that is in a single quadrant and smooth. Actually the quadrant part is not critical, but the smooth part is. The format is `x0 y0 x1 y1 x2 y2` per line, with `x2 y2` of line `i` expected to be equal to `x0 y0` of line `i+1`.

The output is in the same format.

At the highest level, the C++ code produces the bezier sequence with the best score, using dynamic programming to compute the optimum. The score has two components: an error representing deviation from the input curve (so it would be 0 for a matching curve) and a penalty representing the number of points required to represent the curve. Perhaps the most interesting thing about the penalty calculation is that it accounts for the two off-curve point in a row optimization of TrueType.

The error calculation is probably the trickiest part. As in the thesis, it's based on doing a numerical integral of an error metric over the arclength of both the source curve and the candidate bezier. To facilitate fast computation, the `x,y` position and tangent vector of the source curve are stored in an array indexed by arclength, then linear interpolation is used for lookup.

The thesis proposed an error metric based solely on the angle error. This was my first attempt, and, while I found it worked okay, the scaling behavior was not ideal. For long curves (ie sections of low curvature) it would be too tolerant of error, and for short curves (rounded corners with very high curvature) it would fit very tightly. A pure distance metric has the opposite behavior - it will happy cut a rounded corner with a single line segment. So what I ended up with is a weighted sum of L2 norm of angle error and L2 norm of distance error, integrated over the length of the curve.

The dynamic programming algorithm iterates over all quantized grid points near the curve. At each point, it considers drawing a bezier from each previous point to the current point, minimizing the score of all such possibilities. When it reaches the end, you have an optimum curve. There is a small bit of optimization that shortcuts the full search when a solution with two beziers (or fewer) comes under the minimum penalty for a more finely subdivided curve. I thought of ways of pruning the search even more, but I don't think there's much low-hanging fruit.

The off-curve point optimization is interesting to reason about analytically. Consider a curve defined by on-curve points at the endpoints and off-curve points in the interior. Assuming that the tangents match the source curve at knot points (which is the assumption I make), given an off-curve point, the next off-curve point is uniquely determined - it is the reflection of the preceding off-curve point over the tangent point on the curve. A corollary is that there is exactly one such result for each n - the one for which the last tangent point coincides with the endpoint of the source curve.

The dynamic programming optimization reliably finds these sequences, and also finds the cases where the total score can be improved by inserting an on-curve point. These do happen (statistically they seem likely on S curves, not so likely for one quadrant of an O).
