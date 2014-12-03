import argparse
import cv2

import maze
import util
import graphs

def colorType(s):
  try:
    r, g, b = map(int, s.split(','))
    return (r, g, b)
  except:
    raise TypeError

start = None
finish = None

def mouseCallback(event, x, y, flags, params):
  global start, finish
  if event == cv2.EVENT_LBUTTONDOWN and start == None:
    start = (x, y)
  elif event == cv2.EVENT_LBUTTONDOWN and finish == None:
    finish = (x, y)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required = True, help = 'Path to the image')
ap.add_argument('-r', '--rgb', required = False, type = colorType, default = (0, 0, 255), help = 'Red component of color')

ap.add_argument('-b', '--bins', required = False, type = int, default = 8, help = '# of bins when making graph')
ap.add_argument('-c', '--clusters', required = False, type = int, default = 2, help = '# of clusters used in color quantization')

ap.add_argument('--debug', dest = 'debug', action = 'store_true')
ap.add_argument('--no-debug', dest = 'debug', action = 'store_false')
ap.set_defaults(debug = False)

args = vars(ap.parse_args())

# load the image and grab its width and height
image = cv2.imread(args["image"])
original = image.copy()

#image = util.areaResize(image, 640, 480)
(h, w) = image.shape[:2]
 
# quantize image
image = maze.quantizeColors(image, args['clusters'])
image = maze.splitQuantized(image)
image = maze.completeShape(image)
image = maze.makeSkeleton(image)
paths = maze.makePaths(image)
graph = graphs.Graph(paths, binSize = args['bins'])

r, g, b = args['rgb']

if args['debug'] == True:
  for node in graph.neighbors:
    for neighbor in graph.neighbors[node]:
      p1 = graph.nodes[node]
      p2 = graph.nodes[neighbor]
      cv2.line(original, p1, p2, (b, g, r))

cv2.namedWindow('Original Maze')
cv2.imshow('Original Maze', original)

cv2.setMouseCallback('Original Maze', mouseCallback)

while True:
  while finish == None:
    cv2.waitKey(10)

  path = graph.findPath(start, finish)
  start = None
  finish = None
  if path == None:
    continue

  # draw the line over the image
  solved = original.copy()
  for p1, p2 in util.transitions(path):
    cv2.line(solved, p1, p2, (b, g, r), thickness = 2)

  # show the image
  cv2.namedWindow('Solved Maze')
  cv2.imshow('Solved Maze', solved)
  cv2.waitKey(0)
  cv2.destroyWindow('Solved Maze')

