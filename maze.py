from __future__ import division
import cv2
import numpy as np
from sklearn.cluster import MiniBatchKMeans
#import skimage.feature as skfeature

# Splits the image into k colors.
# Any values of k larger than 2 are non-deterministic and can range in results from incredibly good to bad.
# Despite sometimes getting great results w/ k = 8, I encourage a value of 2 because it works well enough all the time.
# Any values of k larger than 2 have a wide range of outcomes, from terrible to amazing.
def quantizeColors(img, k = 2):
  # get height, width of image
  h, w = img.shape[:2]
   
  # reshape the image into a feature vector so that k-means
  # can be applied
  img = img.reshape((img.shape[0] * img.shape[1], 3))
   
  # apply k-means using the specified number of clusters and
  # then create the quantized image based on the predictions
  clt = MiniBatchKMeans(n_clusters = k)
  labels = clt.fit_predict(img)
  quant = clt.cluster_centers_.astype("uint8")[labels]
   
  # reshape the feature vectors to images
  return quant.reshape((h, w, 3))

# Takes an image that was quantized, computes the average color, and thresholds it around that color.
# This extracts the maze from the background, and is necessary in images quantized to more than 2 colors.
def splitQuantized(img):
  levels = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  avgColor = int(cv2.mean(levels)[0])
  retval, result =cv2.threshold(levels, avgColor, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
  return result

# Use a probabilistic hough line transform to fill in the gaps in the maze (result of bad camera).
# Iter can be set as high as wanted without destroying the image, provided the image isn't absolutely terrible.
# It won't close incredibly large gaps, but that was a tradeoff for not destoying the image.
# If that is a problem, take a better picture.  If you can't, get a better camera.
def completeShape(img, iters = 10, minLength = 10, maxLength = 20, votes = 700, color = 255, deg = 1, width = 1):
  lineCanvas = img.copy()

  # The counter "i" is not used, we just need to run this a variable number of times
  # Each run adds more lines that were previously missed.
  # Ten runs seems to be the point of diminishing returns.
  for i in range(0, iters):
    lines = cv2.HoughLinesP(img, 1, deg * 3.14 / 180, votes, minLineLength = minLength, maxLineGap = 5)
    lines = [] if lines == None else lines[0]
    for x1, y1, x2, y2 in lines:
      # There's no way to cull lines longer than some length in HoughLinesP, so I'm doing it here myself.
      if np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < maxLength:
        cv2.line(lineCanvas, (x1, y1), (x2, y2), color, thickness  = width)
  return lineCanvas

# Take the lines computed from the above functions and reduce them down to lines of width 1.
# This helps convert the image into an undirected graph used for solving the maze.
# In order for this to work, the space between the lines NEEDS to be white.
def makeSkeleton(img):
  # Invert colors, because input images should have walls as white and spaces as black.
  _, imgInverse = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)

  # Get the width and height again.
  h, w = img.shape[:2]

  skeleton = np.zeros((h, w), dtype = np.uint8)
  temp = None
  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

  while True:
    temp = cv2.morphologyEx(imgInverse, cv2.MORPH_OPEN, kernel)
    temp = cv2.bitwise_not(temp)
    temp = cv2.bitwise_and(imgInverse, temp)
    skeleton = cv2.bitwise_or(skeleton, temp)
    imgInverse = cv2.erode(imgInverse, kernel)

    _, maxVal, _, _ = cv2.minMaxLoc(imgInverse)
    if maxVal == 0:
      break

  #skeleton = completeShape(skeleton, iters = 1, minLength = 2, maxLength = 50, votes = 50)
  for _ in range(0, 5):
    skeleton = removeNoise(skeleton)
  skeleton = cv2.dilate(skeleton, kernel)
  skeleton = completeShape(skeleton, iters = 30, votes = 1, width = 3, minLength = 8, maxLength = 20, deg = 90)
  #skeleton = cv2.erode(skeleton, kernel)
  return skeleton

# remove pixels that have no neighbors
def removeNoise(img):
  element = np.ones((5, 5), dtype = np.float32) / 25
  test = cv2.filter2D(img, -1, element)
  test = cv2.min(test, img)
  _, test = cv2.threshold(test, 255 / 9 - 1, 255, cv2.THRESH_BINARY)
  return test

def makePaths(img):
  contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
  maxContour = None
  maxContourLen = 0

  h, w = img.shape[:2]
  testOut = np.zeros((h, w), np.uint8)

  lineSegments = []
  for contour in contours:
    lineSegment = []
    for part in contour:
      for x, y in part:
        lineSegment.append((x, y))
    lineSegments.append(lineSegment)

  return lineSegments
'''
def makePaths(img):
  h, w = img.shape[:2]
  pathPad = np.zeros((h, w), np.uint8)

  lines = cv2.HoughLinesP(img, 1, 1 * 3.14 / 180, 20, minLineLength = 10, maxLineGap = 4)
  lines = [] if lines == None else lines[0]
  k = 8
  for x1, y1, x2, y2 in lines:
    cv2.line(pathPad, (x1 - (x1 % k), y1 - (y1 % k)), (x2 - (x2 % k), y2 - (y2 % k)), 255)

  return pathPad
'''
