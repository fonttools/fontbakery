# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.
import math
import robofab.world

from fontTools.misc import bezierTools as rfBezierTools
from bakery_lint.base import BakeryTestCase as TestCase
from robofab.pens.digestPen import DigestPointPen


def _getOnCurves(contour):
    points = set()
    for segment in contour:
        pt = segment.onCurve
        points.add((pt.x, pt.y))
    return points


def _unwrapPoint(pt):
    return pt.x, pt.y


def _testPointNearVerticalMetrics(pt, verticalMetrics):
    y = pt[1]
    for v in verticalMetrics:
        d = abs(v - y)
        if d != 0 and d <= 5:
            return True, v
    return False, None


def _calcAngle(point1, point2, r=None):
    if not isinstance(point1, tuple):
        point1 = _unwrapPoint(point1)
    if not isinstance(point2, tuple):
        point2 = _unwrapPoint(point2)
    width = point2[0] - point1[0]
    height = point2[1] - point1[1]
    angle = round(math.atan2(height, width) * 180 / math.pi, 3)
    if r is not None:
        angle = round(angle, r)
    return angle


def _getAngleOffset(angle, distance):
    A = 90
    B = angle
    C = 180 - (A + B)
    if C == 0:
        return 0
    c = distance
    A = math.radians(A)
    B = math.radians(B)
    C = math.radians(C)
    b = (c * math.sin(B)) / math.sin(C)
    return round(b, 5)


def _intersectLines((a1, a2), (b1, b2)):
    # adapted from: http://www.kevlindev.com/gui/math/intersection/Intersection.js
    ua_t = (b2[0] - b1[0]) * (a1[1] - b1[1]) - (b2[1] - b1[1]) * (a1[0] - b1[0])
    ub_t = (a2[0] - a1[0]) * (a1[1] - b1[1]) - (a2[1] - a1[1]) * (a1[0] - b1[0])
    u_b = (b2[1] - b1[1]) * (a2[0] - a1[0]) - (b2[0] - b1[0]) * (a2[1] - a1[1])
    if u_b != 0:
        ua = ua_t / float(u_b)
        ub = ub_t / float(u_b)
        if 0 <= ua and ua <= 1 and 0 <= ub and ub <= 1:
            return a1[0] + ua * (a2[0] - a1[0]), a1[1] + ua * (a2[1] - a1[1])
        else:
            return None
    else:
        return None


def _getLineLength(pt1, pt2):
    return math.hypot(pt1[0] - pt2[0], pt1[1] - pt2[1])


def _getLineCurveIntersection(line, curve):
    points = curve + line
    # TODO: Need to find bezierTools used in nanny.py
    intersection = rfBezierTools.intersectCubicLine(*points)
    return intersection


def _roundPoint(pt):
    return round(pt[0]), round(pt[1])


def _getUnevenHandleShape(pt0, pt1, pt2, pt3, intersection, start, end, off):
    # TODO: Here we use fontTools bezierTools
    splitSegments = rfBezierTools.splitCubicAtT(pt0, pt1, pt2, pt3, *intersection.t)
    curves = []
    for segment in splitSegments:
        if _roundPoint(segment[0]) != _roundPoint(start) and not curves:
            continue
        curves.append(segment[1:])
        if _roundPoint(segment[-1]) == _roundPoint(end):
            break
    return curves + [off, start]


def _createLineThroughPoint(pt, angle):
    angle = math.radians(angle)
    length = 100000
    x1 = math.cos(angle) * -length + pt[0]
    y1 = math.sin(angle) * -length + pt[1]
    x2 = math.cos(angle) * length + pt[0]
    y2 = math.sin(angle) * length + pt[1]
    return (x1, y1), (x2, y2)


class TestForOverlappingPoints(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_overlapping_points(self):
        """ Consequtive points should not overlap. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            overlappingPoints = {}
            for index, contour in enumerate(glyph):
                if len(contour) == 1:
                    continue
                prev = _unwrapPoint(contour[-1].onCurve)
                for segment in contour:
                    point = _unwrapPoint(segment.onCurve)
                    if point == prev:
                        if index not in overlappingPoints:
                            overlappingPoints[index] = set()
                        overlappingPoints[index].add(point)
                    prev = point
            if overlappingPoints:
                msg = '"{0}" Two or more points are overlapping. {1}'
                self.fail(msg.format(glyph.name, overlappingPoints))


class TestForUnnecessaryPoints(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_unnecessary_points(self):
        """ Consecutive segments shouldn't have the same angle. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            unnecessaryPoints = {}
            for index, contour in enumerate(glyph):
                for segmentIndex, segment in enumerate(contour):
                    if segment.type != "line":
                        continue

                    prevSegment = contour[segmentIndex - 1]
                    nextSegment = contour[(segmentIndex + 1) % len(contour)]
                    if nextSegment.type != "line":
                        continue

                    thisAngle = _calcAngle(prevSegment.onCurve, segment.onCurve)
                    nextAngle = _calcAngle(segment.onCurve, nextSegment.onCurve)
                    if thisAngle == nextAngle:
                        if index not in unnecessaryPoints:
                            unnecessaryPoints[index] = []
                        unnecessaryPoints[index].append(_unwrapPoint(segment.onCurve))

            if unnecessaryPoints:
                msg = '"{0}" One or more unnecessary points are present in lines. {1}'
                self.fail(msg.format(glyph.name, unnecessaryPoints))


class TestForStrayPoints(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_stray_points(self):
        """ There should be no stray points. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            strayPoints = {}
            for index, contour in enumerate(glyph):
                if len(contour) == 1:
                    pt = contour[0].onCurve
                    pt = (pt.x, pt.y)
                    strayPoints[index] = pt
            if strayPoints:
                msg = '"{0}" One or more stray points are present. {1}'
                self.fail(msg.format(glyph.name, strayPoints))


class TestForUnevenHandles(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_uneven_handles(self):
        """ One or more curves has uneven handles. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            unevenHandles = {}
            for index, contour in enumerate(glyph):
                prevPoint = contour[-1].onCurve
                for segment in contour:
                    if segment.type == "curve":
                        # create rays perpendicular to the
                        # angle between the on and off
                        # through the on
                        on1 = _unwrapPoint(prevPoint)
                        off1, off2 = [_unwrapPoint(pt) for pt in segment.offCurve]
                        on2 = _unwrapPoint(segment.onCurve)
                        curve = (on1, off1, off2, on2)
                        off1Angle = _calcAngle(on1, off1) - 90
                        on1Ray = _createLineThroughPoint(on1, off1Angle)
                        off2Angle = _calcAngle(off2, on2) - 90
                        on2Ray = _createLineThroughPoint(on2, off2Angle)
                        # find the intersection of the rays
                        rayIntersection = _intersectLines(on1Ray, on2Ray)
                        if rayIntersection is not None:
                            # draw a line between the off curves and the intersection
                            # and find out where these lines intersect the curve
                            off1Intersection = _getLineCurveIntersection((off1, rayIntersection), curve)
                            off2Intersection = _getLineCurveIntersection((off2, rayIntersection), curve)
                            if off1Intersection is not None and off2Intersection is not None:
                                if off1Intersection.points and off2Intersection.points:
                                    off1IntersectionPoint = (off1Intersection.points[0].x, off1Intersection.points[0].y)
                                    off2IntersectionPoint = (off2Intersection.points[0].x, off2Intersection.points[0].y)
                                    # assemble the off curves and their intersections into lines
                                    off1Line = (off1, off1IntersectionPoint)
                                    off2Line = (off2, off2IntersectionPoint)
                                    # measure and compare these
                                    # if they are not both very short calculate the ratio
                                    length1, length2 = sorted((_getLineLength(*off1Line), _getLineLength(*off2Line)))
                                    if length1 >= 3 and length2 >= 3:
                                        ratio = length2 / float(length1)
                                        # if outside acceptable range, flag
                                        if ratio > 1.5:
                                            off1Shape = _getUnevenHandleShape(on1, off1, off2, on2, off1Intersection, on1, off1IntersectionPoint, off1)
                                            off2Shape = _getUnevenHandleShape(on1, off1, off2, on2, off2Intersection, off2IntersectionPoint, on2, off2)
                                            if index not in unevenHandles:
                                                unevenHandles[index] = []
                                            unevenHandles[index].append((off1, off2, off1Shape, off2Shape))
                    prevPoint = segment.onCurve
            if unevenHandles:
                msg = '{0} one or more curves has uneven handles {1}.'
                self.fail(msg.format(glyph.name, unevenHandles))

class TestForUnnecessaryHandles(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_unnecessary_handles(self):
        """ One or more curves has unnecessary handles. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            unnecessaryHandles = {}
            for index, contour in enumerate(glyph):
                prevPoint = contour[-1].onCurve
                for segment in contour:
                    if segment.type == "curve":
                        pt0 = prevPoint
                        pt1, pt2 = segment.offCurve
                        pt3 = segment.onCurve
                        lineAngle = _calcAngle(pt0, pt3, 0)
                        bcpAngle1 = bcpAngle2 = None
                        if (pt0.x, pt0.y) != (pt1.x, pt1.y):
                            bcpAngle1 = _calcAngle(pt0, pt1, 0)
                        if (pt2.x, pt2.y) != (pt3.x, pt3.y):
                            bcpAngle2 = _calcAngle(pt2, pt3, 0)
                        if bcpAngle1 == lineAngle and bcpAngle2 == lineAngle:
                            if index not in unnecessaryHandles:
                                unnecessaryHandles[index] = []
                            unnecessaryHandles[index].append((_unwrapPoint(pt1), _unwrapPoint(pt2)))
                    prevPoint = segment.onCurve
            if unnecessaryHandles:
                msg = '"{0}" One or more curves has unnecessary handles {1}'
                self.fail(msg.format(glyph.name, unnecessaryHandles))


class TestForCrossedHandles(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_crossed_handles(self):
        """ One or more curves contain crossed handles. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            crossedHandles = {}
            for index, contour in enumerate(glyph):
                pt0 = _unwrapPoint(contour[-1].onCurve)
                for segment in contour:
                    pt3 = _unwrapPoint(segment.onCurve)
                    if segment.type == "curve":
                        pt1, pt2 = [_unwrapPoint(p) for p in segment.offCurve]
                        # direct intersection
                        direct = _intersectLines((pt0, pt1), (pt2, pt3))
                        if direct:
                            if index not in crossedHandles:
                                crossedHandles[index] = []
                            crossedHandles[index].append(dict(points=(pt0, pt1, pt2, pt3), intersection=direct))
                        # indirect intersection
                        else:
                            while 1:
                                # bcp1 = ray, bcp2 = segment
                                angle = _calcAngle(pt0, pt1)
                                if angle in (0, 180.0):
                                    t1 = (pt0[0] + 1000, pt0[1])
                                    t2 = (pt0[0] - 1000, pt0[1])
                                else:
                                    yOffset = _getAngleOffset(angle, 1000)
                                    t1 = (pt0[0] + 1000, pt0[1] + yOffset)
                                    t2 = (pt0[0] - 1000, pt0[1] - yOffset)
                                indirect = _intersectLines((t1, t2), (pt2, pt3))
                                if indirect:
                                    if index not in crossedHandles:
                                        crossedHandles[index] = []
                                    crossedHandles[index].append(dict(points=(pt0, indirect, pt2, pt3), intersection=indirect))
                                    break
                                # bcp1 = segment, bcp2 = ray
                                angle = _calcAngle(pt3, pt2)
                                if angle in (90.0, 270.0):
                                    t1 = (pt3[0], pt3[1] + 1000)
                                    t2 = (pt3[0], pt3[1] - 1000)
                                else:
                                    yOffset = _getAngleOffset(angle, 1000)
                                    t1 = (pt3[0] + 1000, pt3[1] + yOffset)
                                    t2 = (pt3[0] - 1000, pt3[1] - yOffset)
                                indirect = _intersectLines((t1, t2), (pt0, pt1))
                                if indirect:
                                    if index not in crossedHandles:
                                        crossedHandles[index] = []
                                    crossedHandles[index].append(dict(points=(pt0, pt1, indirect, pt3), intersection=indirect))
                                    break
                                break
                    pt0 = pt3

            if crossedHandles:
                msg = '"{0}" One or more curves contain crossed handles: {1}'
                self.fail(msg.format(glyph.name, crossedHandles))


class TestForComplexCurves(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_complex_curves(self):
        """ One or more curves is suspiciously complex. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:

            impliedS = {}
            for index, contour in enumerate(glyph):
                prev = _unwrapPoint(contour[-1].onCurve)
                for segment in contour:
                    if segment.type == "curve":
                        pt0 = prev
                        pt1, pt2 = [_unwrapPoint(p) for p in segment.offCurve]
                        pt3 = _unwrapPoint(segment.onCurve)
                        line1 = (pt0, pt3)
                        line2 = (pt1, pt2)
                        if _intersectLines(line1, line2):
                            if index not in impliedS:
                                impliedS[index] = []
                            impliedS[index].append((prev, pt1, pt2, pt3))
                    prev = _unwrapPoint(segment.onCurve)
            if impliedS:
                msg = 'Some curves in "{0}" are suspicious: {1}'
                self.fail(msg.format(glyph.name, impliedS))


class TestUnsmoothSmooths(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_unsmooth_smooths(self):
        """ Smooth segments should have bcps in the right places. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            unsmoothSmooths = {}
            for index, contour in enumerate(glyph):
                prev = contour[-1]
                for segment in contour:
                    if prev.type == "curve" and segment.type == "curve":
                        if prev.smooth:
                            angle1 = _calcAngle(prev.offCurve[1], prev.onCurve, r=0)
                            angle2 = _calcAngle(prev.onCurve, segment.offCurve[0], r=0)
                            if angle1 != angle2:
                                if index not in unsmoothSmooths:
                                    unsmoothSmooths[index] = []
                                pt1 = _unwrapPoint(prev.offCurve[1])
                                pt2 = _unwrapPoint(prev.onCurve)
                                pt3 = _unwrapPoint(segment.offCurve[0])
                                unsmoothSmooths[index].append((pt1, pt2, pt3))
                    prev = segment
            if unsmoothSmooths:
                self.fail('Smooth segments in "{0}" have bcps in wrong places: {1}'.format(glyph.name, unsmoothSmooths))


class TestForSegmentsNearVerticalMetrics(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_segments_near_vmet(self):
        """ Points shouldn't be just off a vertical metric. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            verticalMetrics = {
                0 : set()
            }
            for attr in "descender xHeight capHeight ascender".split(" "):
                value = getattr(font.info, attr)
                verticalMetrics[value] = set()
            for contour in glyph:
                sequence = None
                # test the last segment to start the sequence
                pt = _unwrapPoint(contour[-1].onCurve)
                near, currentMetric = _testPointNearVerticalMetrics(pt, verticalMetrics)
                if near:
                    sequence = set()
                # test them all
                for segment in contour:
                    pt = _unwrapPoint(segment.onCurve)
                    near, metric = _testPointNearVerticalMetrics(pt, verticalMetrics)
                    # hit on the same metric as the previous point
                    if near and sequence is not None and metric == currentMetric:
                        sequence.add(pt)
                    else:
                        # existing sequence, note it if needed, clear it
                        if sequence:
                            if len(sequence) > 1:
                                verticalMetrics[currentMetric] |= sequence
                        sequence = None
                        currentMetric = None
                        # hit, make a new sequence
                        if near:
                            sequence = set()
                            currentMetric = metric
                            sequence.add(pt)
            for verticalMetric, points in verticalMetrics.items():
                if not points:
                    del verticalMetrics[verticalMetric]

            if verticalMetrics:
                self.fail('Points of glyph "{0}" are off a vertical metrics: {1}'.format(glyph.name, verticalMetrics))


class TestForStraightLines(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_straight_lines(self):
        """ Lines shouldn't be just shy of vertical or horizontal. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:

            straightLines = {}
            for index, contour in enumerate(glyph):
                prev = _unwrapPoint(contour[-1].onCurve)
                for segment in contour:
                    point = _unwrapPoint(segment.onCurve)
                    if segment.type == "line":
                        x = abs(prev[0] - point[0])
                        y = abs(prev[1] - point[1])
                        if x > 0 and x <= 5:
                            if index not in straightLines:
                                straightLines[index] = set()
                            straightLines[index].add((prev, point))
                        if y > 0 and y <= 5:
                            if index not in straightLines:
                                straightLines[index] = set()
                            straightLines[index].add((prev, point))
                    prev = point

            if straightLines:
                self.fail('Glyph {0} has straight lines {1}'.format(glyph.name, straightLines))


class TestForExtremePoints(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_extreme_points(self):
        """ One or more curves need an extreme point. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            pointsAtExtrema = {}
            for index, contour in enumerate(glyph):
                dummy = glyph.copy()
                dummy.clear()
                dummy.appendContour(contour)
                # TODO: RGlyph does not have extremePoints
                #  so need to ask Dave what they are and probably find
                #  opensource decision of function.
                contour.extremePoints()
                testPoints = _getOnCurves(dummy[0])
                points = _getOnCurves(contour)
                if points != testPoints:
                    pointsAtExtrema[index] = testPoints - points
            if pointsAtExtrema:
                msg = '{0} need an extreme point in one or more curves {1}'
                self.fail(msg.format(glyph.name, pointsAtExtrema))


class TestForOpenContours(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_open_contours(self):
        """ One or more contours are not properly closed. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            openContours = {}
            for index, contour in enumerate(glyph):
                if not contour.points or contour.points[0].type == 'move':
                    continue

                start = contour[0].onCurve
                start = (start.x, start.y)
                end = contour[-1].onCurve
                end = (end.x, end.y)
                if start != end:
                    openContours[index] = (start, end)

            if openContours:
                self.fail('{0} has opened contours {1}'.format(glyph.name, openContours))


class TestForSmallContours(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_for_small_contours(self):
        """ One or more contours are suspiciously small. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            smallContours = {}
            for index, contour in enumerate(glyph):
                box = contour.box
                if not box:
                    continue
                xMin, yMin, xMax, yMax = box
                w = xMax - xMin
                h = yMin - yMax
                area = abs(w * h)
                if area <= 4:
                    smallContours[index] = contour.box
            if smallContours:
                self.fail('{0} has suspiciously small contours {1}'.format(glyph.name, smallContours))


class TestDuplicateContours(TestCase):

    targets = ['upstream']
    name = __name__
    tool = 'lint'

    @classmethod
    def skipUnless(cls):
        return not cls.operator.path.endswith('.ufo')

    def test_duplicate_contours(self):
        """ One or more contours are duplicated. """
        font = robofab.world.OpenFont(self.operator.path)

        for glyph in font:
            contours = {}
            for index, contour in enumerate(glyph):
                contour = contour.copy()
                contour.autoStartSegment()
                pen = DigestPointPen()
                contour.drawPoints(pen)
                digest = pen.getDigest()
                if digest not in contours:
                    contours[digest] = []
                contours[digest].append(index)
            duplicateContours = []
            for digest, indexes in contours.items():
                if len(indexes) > 1:
                    duplicateContours.append(indexes[0])
            if duplicateContours:
                self.fail('{0} has duplicated contours {1}'.format(glyph.name, duplicateContours))
