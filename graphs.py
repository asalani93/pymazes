import numpy as np

# Graph library capable of A* pathfinding

class Graph:

  def __init__(self, lineSegments, binSize = 4):
    self.binSize = binSize

    for idx1, lineSegment in enumerate(lineSegments):
      for idx2, p in enumerate(lineSegment):
        x, y = p
        binX = x - (x % binSize) + binSize / 2
        binY = y - (y % binSize) + binSize / 2
        lineSegments[idx1][idx2] = (binX, binY)

    self.nodes = []
    for line in lineSegments:
      for x, y in line:
        if (x, y) not in self.nodes:
          self.nodes.append((x, y))

    self.neighbors = {}
    for line in lineSegments:
      line = zip(line[:-1], line[1:])
      for p1, p2 in line:
        idx1 = self.nodes.index(p1)
        idx2 = self.nodes.index(p2)

        if idx1 not in self.neighbors:
          self.neighbors[idx1] = []

        if idx2 not in self.neighbors:
          self.neighbors[idx2] = []

        if idx2 not in self.neighbors[idx1]:
          self.neighbors[idx1].append(idx2)

        if idx1 not in self.neighbors[idx2]:
          self.neighbors[idx2].append(idx1)

    self.bins = {}
    for i in self.neighbors:
      x = len(self.neighbors[i])
      if x not in self.bins:
        self.bins[x] = 0
      self.bins[x] += 1

  def getClosestNode(self, p, maxDist = 50):
    x, y = p
    binX = x - (x % self.binSize) + self.binSize / 2
    binY = y - (y % self.binSize) + self.binSize / 2

    minDist = maxDist
    minNode = None

    for compX, compY in self.nodes:
      deltaX = abs(binX - compX)
      deltaY = abs(binY - compY)
      dist = np.sqrt(deltaX**2 + deltaY**2)

      if dist < minDist:
        minDist = dist
        minNode = (compX, compY)

    return minNode

  def findPath(self, p1, p2):
    1

  