import heapq
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
    # If a point is given is not an actual node in the graph, find the closest node.
    # If there is no closest node up to a certain distance, fail and claim no path was found.
    if p1 not in self.nodes:
      p1 = self.getClosestNode(p1)
      if p1 == None:
        return None

    # Do the same thing for p2 instead of p1.
    if p2 not in self.nodes:
      p2 = self.getClosestNode(p2)
      if p2 == None:
        return None

    # Actual A* code
    frontier = []  # set of nodes marked to be explored
    explored = []                 # set of nodes already visited
    cameFrom = {}                 # dictionary mapping nodes to parent nodes
    gScore = {}                   # cost along best known path
    fScore = {}                   # cost along best known path plus heuristic

    # Push the starting node on to the frontier
    heapq.heappush(frontier, (0, p1))
    gScore[p1] = 0
    fScore[p1] = gScore[p1] + self.heuristic(p1, p2)

    while len(frontier) > 0:
      _, curr = heapq.heappop(frontier)

      # If curr has already been explored, skip it
      # Due to the optimality constraint of A* heuristics, if curr has been already visited,
      #   there is no way for this visit to curr to be better than the prior visit to curr.
      if curr in explored:
        continue

      # If we're at the goal state, stop and return the path found to the goal.
      if curr == p2:
        return self.rebuildPath(p2, cameFrom)

      # Add curr to explored so we don't hit it again.
      # See comment about optimality to understand why.
      explored.append(curr)

      # Go through every neighbor to curr, and add it to the heap.
      # Duplicates are OK because of optimality + using a priority queue for the heap.
      # The best path to the neighbor will always be visited first.
      for neighbor in self.neighbors[self.nodes.index(curr)]:
        neighbor = self.nodes[neighbor]
        g = gScore[curr] + self.heuristic(curr, neighbor)
        f = g + self.heuristic(curr, p2)

        # If this is the fastest way to get to the neighbor...
        if neighbor not in gScore or g < gScore[neighbor]:
          # Set this as the minimal gScore and fScore to the node, and set the parent to curr.
          gScore[neighbor] = g
          fScore[neighbor] = f
          cameFrom[neighbor] = curr

          # Don't waste cycles putting duplicates into the frontier.
          # You could technically put all nodes here and it would still work, but this is cleaner.
          heapq.heappush(frontier, (f, neighbor))

    # No valid paths found, return None instead.
    return None



  def heuristic(self, p, g):
    # Just the Euclidean distance between the current node and the end node
    return np.sqrt((p[0] - g[0])**2 - (p[1] - g[1])**2)

  def rebuildPath(self, p, parents):
    curr = p
    path = []

    while True:
      # Push current node to front of the list, because it comes before anything else in the list.
      path.insert(0, curr)

      # If this node doesn't have parents, it's the first node and the path is completed.
      if curr not in parents:
        return path

      # Move to the next parent.
      curr = parents[curr]
  