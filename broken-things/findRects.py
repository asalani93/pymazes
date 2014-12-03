from __future__ import division
import sys
import cv2 as cv
import numpy as np
import math

def findRects(mat):
  h, w = mat.shape[:2]
  bw = cv.cvtColor(mat, cv.COLOR_BGR2GRAY)
  bw = cv.cvtColor(bw, cv.COLOR_GRAY2BGR)

  # find edges, make them bigger so HoughLinesP finds longer, contiguous lines
  #edges = cv.Canny(bw, 50, 250)
  edges = cv.Canny(mat, 100, 200)
  element = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3))
  edges = cv.dilate(edges, element)
  edges = cv.erode(edges, element)

  # line segment detection (HoughLinesP detects line segments, HoughLines doesn't)
  minLength = ((h + w) / 2) / 20
  lines = cv.HoughLinesP(edges, 1, 3.14 / 180.0, 70, minLineLength = minLength)
  lines = [] if lines == None else lines[0]

  # take each line and expand it a little in both directions to ensure an intersection
  expandLength = ((h + w) / 2) / 10
  expandedLines = []
  for line in lines:
    expandedLines.append(expandLine(line, expandLength))
    #expandedLines.append(line)

  # computer intersections between lines
  intersections = []
  for idx1, l1 in enumerate(expandedLines):
    for idx2, l2 in enumerate(expandedLines[idx1 + 1:]):
      intersection = intersectLines(l1, l2)
      if intersection != None:
        intersections.append(intersection)

  # compute the convex hull of the intersections

  # find minimum area quad that encloses the convex hull

  # line drawing for debug purposes
  for x1, y1, x2, y2 in expandedLines:
    cv.line(bw, (x1, y1), (x2, y2), (100, 255, 100))

  # point drawing for debug purposes
  for x, y in intersections:
    cv.circle(bw, (x, y), 2, (0, 0, 255), thickness = 2)

  return (edges, bw)

# expandes a line by dist in both directions
def expandLine(line, dist):
  x1, y1, x2, y2 = line
  length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
  # some basic trig to expand the lines out by a little bit
  nx1 = int(x2 + (x2 - x1) / length * dist)
  ny1 = int(y2 + (y2 - y1) / length * dist)
  nx2 = int(x1 + (x1 - x2) / length * dist)
  ny2 = int(y1 + (y1 - y2) / length * dist)
  return [nx1, ny1, nx2, ny2]

# compute intersection of two lines, returns pair or None if no intersection found
# source: https://github.com/pgkelley4/line-segments-intersect/blob/master/js/line-segments-intersect.js
# source: http://stackoverflow.com/a/1968345/4266578
def intersectLines(l1, l2):
  x1, y1, x2, y2 = l1
  x3, y3, x4, y4 = l2

  dx1 = x2 - x1; dy1 = y2 - y1
  dx2 = x4 - x3; dy2 = y4 - y3

  if -dx2 * dy1 + dx1 * dy2 == 0:
    return None

  s = (-dy1 * (x1 - x3) + dx1 * (y1 - y3)) / (-dx2 * dy1 + dx1 * dy2)
  t = ( dx2 * (y1 - y3) - dy2 * (x1 - x3)) / (-dx2 * dy1 + dx1 * dy2)

  if 0 <= s <= 1 and 0 <= t <= 1:
    ix = x1 + (t * dx1)
    iy = y1 + (t * dy1)
    return (int(ix), int(iy))
  return None

# compute convex hull, return list of points along convex hull, using graham scan
# source: http://en.wikipedia.org/wiki/Graham_scan
def convexHull(points):
  1


if __name__ == '__main__':
  if len(sys.argv) == 2:
    inImg = cv.imread(sys.argv[1])
    outImg = findRects(inImg)
    cv.imshow('A', outImg)
    cv.waitKey(0)
  else:
    camera = cv.VideoCapture(0)
    cv.namedWindow('EDGES')
    cv.namedWindow('LINES')
    while True:
      _, img = camera.read()
      edges, bw = findRects(img)
      cv.imshow('EDGES', edges)
      cv.imshow('LINES', bw)
      key = cv.waitKey(10)
      if key == 27 or key == 113:
        break


