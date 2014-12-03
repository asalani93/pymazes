import argparse
import cv2

import maze
import util
import graphs
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
ap.add_argument("-c", "--clusters", required = True, type = int, help = "# of clusters")
args = vars(ap.parse_args())

# load the image and grab its width and height
image = cv2.imread(args["image"])
backup = image.copy()
#image = util.areaResize(image, 640, 480)
(h, w) = image.shape[:2]
 
# quantize image
image = maze.quantizeColors(image, args['clusters'])
image = maze.splitQuantized(image)
image = maze.completeShape(image)
#image = cv2.bitwise_not(image)
#image = zhangsuen.computeAB(image)
image = maze.makeSkeleton(image)
paths = maze.makePaths(image)

graph = graphs.Graph(paths, binSize = 4)
#print graph.getClosestNode((300, 200))

start = (190, 220)
finish = (635, 380)
path = graph.findPath(start, finish)

for p1, p2 in util.transitions(path):
  cv2.line(backup, p1, p2, (255, 0, 0), thickness = 2)


'''
image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
image = cv2.subtract(backup, image)
'''

# show the image
cv2.namedWindow('A')
cv2.imshow('A', backup)
cv2.waitKey(0)
