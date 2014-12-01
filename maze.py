from __future__ import division
import sys
import cv2
import numpy
import math

import util

def extractMaze(img):
  WIDTH = 640
  HEIGHT = 480
  THRESHOLD = 0.9
  CTHRESH = 50

  # resize provided image to something sane to make results more uniform
  img = util.areaResize(img, WIDTH, HEIGHT)

  # compute basic info about the image
  h, w = img.shape[:2]
  print w, h
  imgRange = [(x // w, x % w) for x in range(0, w * h)]

  # matrix to use for segmentation, initialize to all zeros
  # a zero represents a pixel that may or may not have a wall in the maze
  # a one represents a pixel that the system is confident is an edge
  seg = numpy.zeros(img.shape[:2])

  # convert to black/white, then to edges
  # edges get passed through dilation/erosion to remove erroneous detections
  bwh = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  can = cv2.Canny(bwh, 100, 200)
  dilater = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
  eroder = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
  can = cv2.dilate(can, dilater)
  can = cv2.erode(can, eroder)

  # find line segments in image
  # these don't need to be 100% encompassing or optimally covering the maze
  # ... provided there are an insignificant amount of false positives
  lines = cv2.HoughLinesP(can, 1, 3.14 / 180, 50)
  lines = [] if lines == None else lines[0]

  # use these line segments to seed the matrix used for image segmentation
  # if everything worked, the image used for segmentation should now have
  # white squares on guaranteed maze edges
  for x1, y1, x2, y2 in lines:
    cv2.line(seg, (x1, y1), (x2, y2), (255, 255, 255))

  # compute the average color of populated pixels
  accum = (0, 0, 0)
  accumCount = 0.01
  for rIdx, cIdx in imgRange:
    if seg[rIdx][cIdx] > THRESHOLD:
      accumCount += 1
      b, g, r = img[rIdx][cIdx]
      accum = (accum[0] + b, accum[1] + g, accum[2] + r)
  averageColor = (accum[0] / accumCount, accum[1] / accumCount, accum[2] / accumCount)

  # run a loop that segments the image until few changes are made in one iteration
  # a step in the loop goes through each "off" pixel in the segmentation image
  # and uses the x, y coords to a) find # of "on" neighbors and b) compute the
  # color distance between the pixel and each known good pixel, as well as comparison
  # to the average color from the initial hough transform
  newSeeds = None
  minSeeds = 20
  iterNum = 0

  # TODO: Iterate from top left, top right, bottom left, bottom right in that order
  # instead of looping until minimal changes
  while newSeeds == None or newSeeds > minSeeds:
    iterNum += 1
    print 'ITERATION:', iterNum, '- CHANGED:', newSeeds
    newSeeds = 0
    newSeg = seg.copy()
    for rIdx, cIdx in imgRange:
      if seg[rIdx][cIdx] > THRESHOLD:
        continue
      for i, j in gridNeighbors((cIdx, rIdx), w, h, 2):
        if seg[rIdx + j][cIdx + i] > THRESHOLD and compareColors(img[rIdx][cIdx], averageColor, CTHRESH):
          newSeg[rIdx][cIdx] = 1.0
          newSeeds += 1
          break
    seg = newSeg


  # once the edges of the maze have been determined, run the maze through a feature
  # detector to find important parts of the maze - these will be used to construct a
  # graph representing the maze

  return seg

def gridNeighbors(pos, w, h, dist):
  x, y = pos
  neighbors = []
  for i in range(-dist, dist):
    for j in range(-dist, dist):
      if 0 <= x + i < w and 0 <= y + j < h:
        neighbors.append((i, j))
  return neighbors

# compares if two colors are within a certain range of each other
def compareColors(col1, col2, maxDif):
  r1, g1, b1 = col1
  r2, g2, b2 = col2

  newCol = (abs(r1 - r2), abs(g1 - g2), abs(b1 - b2))
  avgDif = (newCol[0] + newCol[1] + newCol[2]) / 3
  return avgDif <= maxDif 
