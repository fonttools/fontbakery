# TODO: implement tests with bakery

import re
import math

from fontTools.misc import bezierTools as ftBezierTools
from fontTools.agl import AGL2UV
from fontTools.pens.cocoaPen import CocoaPen
from robofab.pens.digestPen import DigestPointPen
from lib.tools import bezierTools as rfBezierTools


def registerTest():
    pass

# Extreme Points

def testForExtremePoints(glyph):
    """
    Points should be at the extrema.
    """
    pointsAtExtrema = {}
    for index, contour in enumerate(glyph):
        dummy = glyph.copy()
        dummy.clear()
        dummy.appendContour(contour)
        dummy.extremePoints()
        testPoints = _getOnCurves(dummy[0])
        points = _getOnCurves(contour)
        if points != testPoints:
            pointsAtExtrema[index] = testPoints - points
    return pointsAtExtrema

def drawExtremePoints(contours, scale, glyph):
    color = colorInsert()
    path = NSBezierPath.bezierPath()
    d = 16 * scale
    h = d / 2.0
    o = 3 * scale
    for contourIndex, points in contours.items():
        for (x, y) in points:
            r = ((x - h, y - h), (d, d))
            path.appendBezierPathWithOvalInRect_(r)
            path.moveToPoint_((x - h + o, y))
            path.lineToPoint_((x + h - o, y))
            path.moveToPoint_((x, y - h + o))
            path.lineToPoint_((x, y + h - o))
            drawString((x, y - (16 * scale)), "Insert Point", 10, scale, color)
    color.set()
    path.setLineWidth_(scale)
    path.stroke()

registerTest(
    identifier="extremePoints",
    level="contour",
    title="Extreme Points",
    description="One or more curves need an extreme point.",
    testFunction=testForExtremePoints,
    drawingFunction=drawExtremePoints
)


# -------------------
# Segment Level Tests
# -------------------

def testForStraightLines(glyph):
    """
    Lines shouldn't be just shy of vertical or horizontal.
    """
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
    return straightLines

def drawStraightLines(contours, scale, glyph):
    color = colorReview()
    color.set()
    for contourIndex, segments in contours.items():
        for segment in segments:
            xs = []
            ys = []
            for (x, y) in segment:
                xs.append(x)
                ys.append(y)
            xMin = min(xs)
            xMax = max(xs)
            yMin = min(ys)
            yMax = max(ys)
            w = xMax - xMin
            h = yMax - yMin
            r = ((xMin, yMin), (w, h))
            r = NSInsetRect(r, -2 * scale, -2 * scale)
            NSRectFillUsingOperation(r, NSCompositeSourceOver)

registerTest(
    identifier="straightLines",
    level="segment",
    title="Straight Lines",
    description="One or more lines is a few units from being horizontal or vertical.",
    testFunction=testForStraightLines,
    drawingFunction=drawStraightLines
)

# Segments Near Vertical Metrics

def testForSegmentsNearVerticalMetrics(glyph):
    """
    Points shouldn't be just off a vertical metric.
    """
    font = glyph.getParent()
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
    return verticalMetrics

def _testPointNearVerticalMetrics(pt, verticalMetrics):
    y = pt[1]
    for v in verticalMetrics:
        d = abs(v - y)
        if d != 0 and d <= 5:
            return True, v
    return False, None

def drawSegmentsNearVericalMetrics(verticalMetrics, scale, glyph):
    color = colorReview()
    path = NSBezierPath.bezierPath()
    for verticalMetric, points in verticalMetrics.items():
        xMin = None
        xMax = None
        for (x, y) in points:
            path.moveToPoint_((x, y))
            path.lineToPoint_((x, verticalMetric))
            if xMin is None:
                xMin = x
            elif xMin > x:
                xMin = x
            if xMax is None:
                xMax = x
            elif xMax < x:
                xMax = x
        path.moveToPoint_((xMin, verticalMetric))
        path.lineToPoint_((xMax, verticalMetric))
    color.set()
    path.setLineWidth_(4 * scale)
    path.stroke()

registerTest(
    identifier="pointsNearVerticalMetrics",
    level="segment",
    title="Near Vertical Metrics",
    description="Two or more points are just off a vertical metric.",
    testFunction=testForSegmentsNearVerticalMetrics,
    drawingFunction=drawSegmentsNearVericalMetrics
)

# Unsmooth Smooths

def testUnsmoothSmooths(glyph):
    """
    Smooth segments should have bcps in the right places.
    """
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
    return unsmoothSmooths

def drawUnsmoothSmooths(contours, scale, glyph):
    color = colorReview()
    color.set()
    for contourIndex, points in contours.items():
        path = NSBezierPath.bezierPath()
        for pt1, pt2, pt3 in points:
            path.moveToPoint_(pt1)
            path.lineToPoint_(pt3)
        path.setLineWidth_(2 * scale)
        path.stroke()
        x, y = pt2
        drawString((x, y - (10 * scale)), "Unsmooth Smooth", 10, scale, color, backgroundColor=NSColor.whiteColor())

registerTest(
    identifier="unsmoothSmooths",
    level="segment",
    title="Unsmooth Smooths",
    description="One or more smooth points do not have handles that are properly placed.",
    testFunction=testUnsmoothSmooths,
    drawingFunction=drawUnsmoothSmooths
)

# Complex Curves

def testForComplexCurves(glyph):
    """
    S curves are suspicious.
    """
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
    return impliedS

def drawComplexCurves(contours, scale, glyph):
    color = colorReview()
    color.set()
    for contourIndex, segments in contours.items():
        for segment in segments:
            pt0, pt1, pt2, pt3 = segment
            path = NSBezierPath.bezierPath()
            path.moveToPoint_(pt0)
            path.curveToPoint_controlPoint1_controlPoint2_(pt3, pt1, pt2)
            path.setLineWidth_(3 * scale)
            path.setLineCapStyle_(NSRoundLineCapStyle)
            path.stroke()
            mid = ftBezierTools.splitCubicAtT(pt0, pt1, pt2, pt3, 0.5)[0][-1]
            drawString(mid, "Complex Curve", 10, scale, color, backgroundColor=NSColor.whiteColor())

registerTest(
    identifier="complexCurves",
    level="segment",
    title="Complex Curves",
    description="One or more curves is suspiciously complex.",
    testFunction=testForComplexCurves,
    drawingFunction=drawComplexCurves
)

# Crossed Handles

def testForCrossedHandles(glyph):
    """
    Handles shouldn't intersect.
    """
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
    return crossedHandles

def drawCrossedHandles(contours, scale, glyph):
    d = 10 * scale
    h = d / 2.0
    color = colorReview()
    color.set()
    for contourIndex, segments in contours.items():
        for segment in segments:
            pt1, pt2, pt3, pt4 = segment["points"]
            pt5 = segment["intersection"]
            path1 = NSBezierPath.bezierPath()
            path2 = NSBezierPath.bezierPath()
            path1.moveToPoint_(pt1)
            path1.lineToPoint_(pt2)
            path1.moveToPoint_(pt3)
            path1.lineToPoint_(pt4)
            x, y = pt5
            r = ((x - h, y - h), (d, d))
            path2.appendBezierPathWithOvalInRect_(r)
            path1.setLineWidth_(3 * scale)
            path1.setLineCapStyle_(NSRoundLineCapStyle)
            path1.stroke()
            path2.fill()
            drawString((x, y - (12 * scale)), "Crossed Handles", 10, scale, color, backgroundColor=NSColor.whiteColor())

registerTest(
    identifier="crossedHandles",
    level="segment",
    title="Crossed Handles",
    description="One or more curves contain crossed handles.",
    testFunction=testForCrossedHandles,
    drawingFunction=drawCrossedHandles
)

# Unnecessary Handles

def testForUnnecessaryHandles(glyph):
    """
    Handles shouldn't be used if they aren't doing anything.
    """
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
    return unnecessaryHandles

def drawUnnecessaryHandles(contours, scale, glyph):
    color = colorRemove()
    color.set()
    d = 10 * scale
    h = d / 2.0
    for contourIndex, points in contours.items():
        for bcp1, bcp2 in points:
            # line
            path1 = NSBezierPath.bezierPath()
            path1.moveToPoint_(bcp1)
            path1.lineToPoint_(bcp2)
            path1.setLineWidth_(3 * scale)
            path1.stroke()
            # dots
            path2 = NSBezierPath.bezierPath()
            for (x, y) in (bcp1, bcp2):
                r = ((x - h, y - h), (d, d))
                path2.appendBezierPathWithOvalInRect_(r)
            path2.setLineWidth_(scale)
            path2.stroke()
            # text
            mid = calcMid(bcp1, bcp2)
            drawString(mid, "Unnecessary Handles", 10, scale, color, backgroundColor=NSColor.whiteColor())

registerTest(
    identifier="unnecessaryHandles",
    level="segment",
    title="Unnecessary Handles",
    description="One or more curves has unnecessary handles.",
    testFunction=testForUnnecessaryHandles,
    drawingFunction=drawUnnecessaryHandles
)

# Uneven Handles

def testForUnevenHandles(glyph):
    """
    Handles should share the workload as evenly as possible.
    """
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
    return unevenHandles

def _getUnevenHandleShape(pt0, pt1, pt2, pt3, intersection, start, end, off):
    splitSegments = ftBezierTools.splitCubicAtT(pt0, pt1, pt2, pt3, *intersection.t)
    curves = []
    for segment in splitSegments:
        if _roundPoint(segment[0]) != _roundPoint(start) and not curves:
            continue
        curves.append(segment[1:])
        if _roundPoint(segment[-1]) == _roundPoint(end):
            break
    return curves + [off, start]

def drawUnevenHandles(contours, scale, glyph):
    strokeColor = colorReview()
    fillColor = modifyColorAlpha(strokeColor, 0.15)
    for index, groups in contours.items():
        for off1, off2, shape1, shape2 in groups:
            fillColor.set()
            path = NSBezierPath.bezierPath()
            for shape in (shape1, shape2):
                path.moveToPoint_(shape[-1])
                for curve in shape[:-2]:
                    pt1, pt2, pt3 = curve
                    path.curveToPoint_controlPoint1_controlPoint2_(pt3, pt1, pt2)
                path.lineToPoint_(shape[-2])
                path.lineToPoint_(shape[-1])
            path.fill()
            strokeColor.set()
            path = NSBezierPath.bezierPath()
            path.moveToPoint_(off1)
            path.lineToPoint_(off2)
            path.setLineWidth_(scale)
            path.stroke()
            mid = calcMid(off1, off2)
            drawString(mid, "Uneven Handles", 10, scale, strokeColor, backgroundColor=NSColor.whiteColor())

registerTest(
    identifier="unevenHandles",
    level="segment",
    title="Uneven Handles",
    description="One or more curves has uneven handles.",
    testFunction=testForUnevenHandles,
    drawingFunction=drawUnevenHandles
)

# -----------------
# Point Level Tests
# -----------------

# Stray Points

def testForStrayPoints(glyph):
    """
    There should be no stray points.
    """
    strayPoints = {}
    for index, contour in enumerate(glyph):
        if len(contour) == 1:
            pt = contour[0].onCurve
            pt = (pt.x, pt.y)
            strayPoints[index] = pt
    return strayPoints

def drawStrayPoints(contours, scale, glyph):
    color = colorRemove()
    path = NSBezierPath.bezierPath()
    d = 20 * scale
    h = d / 2.0
    for contourIndex, (x, y) in contours.items():
        r = ((x - h, y - h), (d, d))
        path.appendBezierPathWithOvalInRect_(r)
        drawString((x, y - d), "Stray Point", 10, scale, color)
    color.set()
    path.setLineWidth_(scale)
    path.stroke()

registerTest(
    identifier="strayPoints",
    level="point",
    title="Stray Points",
    description="One or more stray points are present.",
    testFunction=testForStrayPoints,
    drawingFunction=drawStrayPoints
)

# Unnecessary Points

def testForUnnecessaryPoints(glyph):
    """
    Consecutive segments shouldn't have the same angle.
    """
    unnecessaryPoints = {}
    for index, contour in enumerate(glyph):
        for segmentIndex, segment in enumerate(contour):
            if segment.type == "line":
                prevSegment = contour[segmentIndex - 1]
                nextSegment = contour[(segmentIndex + 1) % len(contour)]
                if nextSegment.type == "line":
                    thisAngle = _calcAngle(prevSegment.onCurve, segment.onCurve)
                    nextAngle = _calcAngle(segment.onCurve, nextSegment.onCurve)
                    if thisAngle == nextAngle:
                        if index not in unnecessaryPoints:
                            unnecessaryPoints[index] = []
                        unnecessaryPoints[index].append(_unwrapPoint(segment.onCurve))
    return unnecessaryPoints

def drawUnnecessaryPoints(contours, scale, glyph):
    color = colorRemove()
    path = NSBezierPath.bezierPath()
    for contourIndex, points in contours.items():
        for pt in points:
            drawDeleteMark(pt, scale, path)
            x, y = pt
            drawString((x, y - (10 * scale)), "Unnecessary Point", 10, scale, color)
    color.set()
    path.setLineWidth_(2 * scale)
    path.stroke()

registerTest(
    identifier="unnecessaryPoints",
    level="point",
    title="Unnecessary Points",
    description="One or more unnecessary points are present in lines.",
    testFunction=testForUnnecessaryPoints,
    drawingFunction=drawUnnecessaryPoints
)

# Overlapping Points

def testForOverlappingPoints(glyph):
    """
    Consequtive points should not overlap.
    """
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
    return overlappingPoints

def drawOverlappingPoints(contours, scale, glyph):
    color = colorRemove()
    path = NSBezierPath.bezierPath()
    d = 10 * scale
    h = d / 2.0
    q = h / 2.0
    for contourIndex, points in contours.items():
        for (x, y) in points:
            r = ((x - d + q, y - q), (d, d))
            path.appendBezierPathWithOvalInRect_(r)
            r = ((x - q, y - d + q), (d, d))
            path.appendBezierPathWithOvalInRect_(r)
            drawString((x, y - (12 * scale)), "Overlapping Points", 10, scale, color)
    color.set()
    path.fill()

registerTest(
    identifier="overlappingPoints",
    level="point",
    title="Overlapping Points",
    description="Two or more points are overlapping.",
    testFunction=testForOverlappingPoints,
    drawingFunction=drawOverlappingPoints
)


# --------------
# Test Utilities
# --------------

def _getOnCurves(contour):
    points = set()
    for segement in contour:
        pt = segement.onCurve
        points.add((pt.x, pt.y))
    return points

def _unwrapPoint(pt):
    return pt.x, pt.y

def _roundPoint(pt):
    return round(pt[0]), round(pt[1])

def _intersectLines((a1, a2), (b1, b2)):
    # adapted from: http://www.kevlindev.com/gui/math/intersection/Intersection.js
    ua_t = (b2[0] - b1[0]) * (a1[1] - b1[1]) - (b2[1] - b1[1]) * (a1[0] - b1[0])
    ub_t = (a2[0] - a1[0]) * (a1[1] - b1[1]) - (a2[1] - a1[1]) * (a1[0] - b1[0])
    u_b  = (b2[1] - b1[1]) * (a2[0] - a1[0]) - (b2[0] - b1[0]) * (a2[1] - a1[1])
    if u_b != 0:
        ua = ua_t / float(u_b)
        ub = ub_t / float(u_b)
        if 0 <= ua and ua <= 1 and 0 <= ub and ub <= 1:
            return a1[0] + ua * (a2[0] - a1[0]), a1[1] + ua * (a2[1] - a1[1])
        else:
            return None
    else:
        return None

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

def _createLineThroughPoint(pt, angle):
    angle = math.radians(angle)
    length = 100000
    x1 = math.cos(angle) * -length + pt[0]
    y1 = math.sin(angle) * -length + pt[1]
    x2 = math.cos(angle) * length + pt[0]
    y2 = math.sin(angle) * length + pt[1]
    return (x1, y1), (x2, y2)

def _getLineLength(pt1, pt2):
    return math.hypot(pt1[0] - pt2[0], pt1[1] - pt2[1])

def _getAreaOfTriangle(pt1, pt2, pt3):
    a = _getLineLength(pt1, pt2)
    b = _getLineLength(pt2, pt3)
    c = _getLineLength(pt3, pt1)
    s = (a + b + c) / 2.0
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    return area

def _getLineCurveIntersection(line, curve):
    points = curve + line
    intersection = rfBezierTools.intersectCubicLine(*points)
    return intersection

# -----------------
# Drawing Utilities
# -----------------

def drawDeleteMark(pt, scale, path):
    h = 6 * scale
    x, y = pt
    x1 = x - h
    x2 = x + h
    y1 = y - h
    y2 = y + h
    path.moveToPoint_((x1, y1))
    path.lineToPoint_((x2, y2))
    path.moveToPoint_((x1, y2))
    path.lineToPoint_((x2, y1))

def drawString(pt, text, size, scale, color, alignment="center", backgroundColor=None):
    attributes = attributes = {
        NSFontAttributeName : NSFont.fontWithName_size_("Lucida Grande", size * scale),
        NSForegroundColorAttributeName : color
    }
    if backgroundColor is not None:
        text = " " + text + " "
        attributes[NSBackgroundColorAttributeName] = backgroundColor
    text = NSAttributedString.alloc().initWithString_attributes_(text, attributes)
    x, y = pt
    if alignment == "center":
        width, height = text.size()
        x -= width / 2.0
        y -= height / 2.0
    elif alignment == "right":
        width, height = text.size()
        x -= width
    text.drawAtPoint_((x, y))

def calcMid(pt1, pt2):
    x1, y1 = pt1
    x2, y2 = pt2
    x = x1 - ((x1 - x2) / 2)
    y = y1 - ((y1 - y2) / 2)
    return x, y


if __name__ == "__main__":
    # register the factory
    if roboFontVersion > "1.5.1":
        _registerFactory()
    # sanity check to make sure that the tests are consistently registered
    assert set(reportOrder) == set(testRegistry.keys())
    assert set(drawingOrder) == set(testRegistry.keys())
    # register the defaults
    registerGlyphNannyDefaults()
    # boot the observer
    glyphNannyObserver = GlyphNannyObserver()
    # if debugging, kill any instances of this observer that are already running
    if DEBUG:
        from lib.eventTools.eventManager import allObservers
        for event, observer in allObservers():
            if observer.__class__.__name__ == "GlyphNannyObserver":
                unregisterGlyphNannyObserver(observer)
    # register it
    registerGlyphNannyObserver(glyphNannyObserver)
    # if debugging, show the windows
    if DEBUG:
        GlyphNannyPrefsWindow()
        GlyphNannyTestFontsWindow()
