from __future__ import division
import sys
import cv2 as cv
import numpy as np
import math

import maze

if __name__ == '__main__':
  cv.namedWindow('A')
  key = 0
  if len(sys.argv) == 2:
    inImg = cv.imread(sys.argv[1])
    inImg = maze.extractMaze(inImg)
    while key != 27 and key != 113:
      cv.imshow('A', inImg)
      key = cv.waitKey(10)
  else:
    camera = cv.VideoCapture(0)
    while key != 27 and key != 113:
      _, inImg = camera.read()
      inImg = maze.extractMaze(inImg)
      cv.imshow('A', inImg)
      key = cv.waitKey(10)