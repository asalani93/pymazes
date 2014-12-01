from __future__ import division
import sys
import cv2
import numpy
import math

def areaResize(img, x, y):
  area1 = x * y

  h, w = img.shape[:2]
  area2 = w * h

  ratio = math.sqrt(area1 / area2)
  newHeight = int(h * ratio)
  newWidth = int(w * ratio)

  newImg = cv2.resize(img, (newWidth, newHeight))
  return newImg