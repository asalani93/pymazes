from __future__ import division
import cv2
import numpy as np

# File for implementation of Zhang Suen's image thinning algorithm

# computes a two-channel matrix for the A and B functions
def computeAB(img):
  r, c = img.shape[:2]

  for row in img[1: r - 1]:
    for col in img[1: c - 1]:
      img[row][col] = 128

  return img

def ZhangSuen(img):
  1
