# TODO: implement tests with bakery

import re
import math

from fontTools.misc import bezierTools as ftBezierTools
from fontTools.agl import AGL2UV
from fontTools.pens.cocoaPen import CocoaPen
from robofab.pens.digestPen import DigestPointPen
from lib.tools import bezierTools as rfBezierTools

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
