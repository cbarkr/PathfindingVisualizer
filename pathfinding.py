import pygame
import pygame_menu
import math
import time
from queue import PriorityQueue

"""
Window Setup
"""
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Algorithms")

"""
Colours
"""
white = (255, 255, 255)
black = (0, 0, 0)
purple1 = (128, 0, 128)
blue = (1, 255, 255)
mint = (1, 255, 195)
pink = (255, 179, 253)
purple2 = (157, 114, 255)
grey = (192, 192, 192)

"""
Node Class
"""
class Node:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.width = width
		self.x = row * width
		self.y = col * width
		self.color = grey
		self.neighbour = []
		self.total_rows = total_rows

	def getPos(self):
		return self.row, self.col

	def isClosed(self):
		return self.color == pink

	def isOpen(self):
		return self.color == blue

	def isWall(self):
		return self.color == black

	def isStart(self):
		return self.color == mint

	def isEnd(self):
		return self.color == purple2

	def reset(self):
		return self.color == grey

	def setStart(self):
		self.color = mint

	def setEnd(self):
		self.color = purple2

	def setClosed(self):
		self.color = pink

	def setOpen(self):
		self.color = blue

	def setWall(self):
		self.color = black

	def setPath(self):
		self.color = purple1

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def updateNeighbour(self, grid):
		self.neighbour = []
		if self.row > 0 and not grid[self.row - 1][self.col].isWall():						#	North
			self.neighbour.append(grid[self.row - 1][self.col])

		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isWall():	#	South
			self.neighbour.append(grid[self.row + 1][self.col])
		
		if self.col > 0 and not grid[self.row][self.col - 1].isWall():						#	East
			self.neighbour.append(grid[self.row][self.col - 1])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isWall():	#	West
			self.neighbour.append(grid[self.row][self.col + 1])

	def __lt__(self, other):
		return False

"""
Graph Class
"""
class Graph:
	def constructPath(cameFrom, curr, draw):
		count = 0
		while curr in cameFrom:
			count += 1
			curr = cameFrom[curr]
			curr.setPath()
			draw()
		print("Path is " + str(count) + " nodes long")

	def setGrid(rows, width):
		grid = []
		gap = width // rows
		for i in range(rows):
			grid.append([])
			for j in range(rows):
				node = Node(i, j, gap, rows)
				grid[i].append(node)
		return grid

	def drawGrid(win, rows, width):
		gap = width // rows
		for i in range(rows):
			pygame.draw.line(win, white, (0, i * gap), (width, i * gap))
			pygame.draw.line(win, white, (i * gap, 0), (i * gap, width))

	def draw(win, grid, rows, width):
		win.fill(white)
		for row in grid:
			for node in row:
				node.draw(win)
		Graph.drawGrid(win, rows, width)
		pygame.display.update()

	def getCLickPos(pos, rows, width):
		gap = width // rows
		y, x = pos
		row = y // gap
		col = x // gap
		return row, col

	def heuristic(point1, point2):	#	Return Manhattan distance
		x1, y1 = point1
		x2, y2 = point2
		return abs(x1 - x2) + abs(y1 - y2)

	def astar(draw, grid, start, end):
		untraversedSet = PriorityQueue()	#	Untraversed nodes
		untraversedSet.put((0, start))

		traversedSet = {start}	#	Traversed nodes

		cameFrom = {}	#	Previous nodes

		currentCost = {}
		for row in grid:
			for point in row:
				currentCost[point] = float("inf")	#	Initially set every entry to infinity
		currentCost[start] = 0

		priorityCost = {}
		for row in grid:
			for point in row:
				priorityCost[point] = float("inf")	#	Initially set every entry to infinity
		priorityCost[start] = Graph.heuristic(start.getPos(), end.getPos())

		while not untraversedSet.empty():
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			currentNode = untraversedSet.get()[1]	#	Retrieve node from set
			traversedSet.remove(currentNode)	#	Keep track of traversed nodes by removing from other set

			if currentNode == end:
				Graph.constructPath(cameFrom, end, draw)
				end.setEnd()
				return True

			for node in currentNode.neighbour:
				newCost = currentCost[currentNode] + 1

				if newCost < currentCost[node]:
					cameFrom[node] = currentNode
					currentCost[node] = newCost
					priorityCost[node] = newCost + Graph.heuristic(node.getPos(), end.getPos())

					if node not in traversedSet:
						untraversedSet.put((priorityCost[node], node))
						traversedSet.add(node)
						node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		return False

	def dijkstra(draw, grid, start, end):
		untraversedSet = PriorityQueue()	#	Untraversed nodes
		untraversedSet.put((0, start))

		traversedSet = {start}	#	Traversed nodes

		cameFrom = {}	#	Previous nodes

		currentCost = {}
		for row in grid:
			for point in row:
				currentCost[point] = float("inf")	#	Initially set every entry to infinity
		currentCost[start] = 0

		priorityCost = {}
		for row in grid:
			for point in row:
				priorityCost[point] = float("inf")	#	Initially set every entry to infinity
		priorityCost[start] = 0

		while not untraversedSet.empty():
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			currentNode = untraversedSet.get()[1]
			traversedSet.remove(currentNode)

			if currentNode == end:
				Graph.constructPath(cameFrom, end, draw)
				end.setEnd()
				return True

			for node in currentNode.neighbour:
				newCost = currentCost[currentNode] + 1

				if newCost < currentCost[node]:
					cameFrom[node] = currentNode
					currentCost[node] = newCost
					priorityCost[node] = newCost

					if node not in traversedSet:
						untraversedSet.put((priorityCost[node], node))
						traversedSet.add(node)
						node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		return False
"""
Main
"""
def main(win, width):
	ROWS = 50
	grid = Graph.setGrid(ROWS, width)
	start = None
	end = None
	run = True
	while run:
		Graph.draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]:	# 0 == left mouse
				pos = pygame.mouse.get_pos()
				row, col = Graph.getCLickPos(pos, ROWS, width)
				node = grid[row][col]
				if not start and node != end:
					start = node
					start.setStart()
				elif not end and node != start:
					end = node
					end.setEnd()
				elif node != end and node != start:
					node.setWall()

			elif pygame.mouse.get_pressed()[2]:	# 2 == right mouse
				pos = pygame.mouse.get_pos()
				row, col = Graph.getCLickPos(pos, ROWS, width)
				node = grid[row][col]
				node.reset()
				if node == start:
					node.color = grey
					start = None
				elif node == end:
					node.color = grey
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame. K_SPACE and start and end:
					tic = time.perf_counter()
					for row in grid:
						for spot in row:
							spot.updateNeighbour(grid)

					inDraw = lambda: Graph.draw(win, grid, ROWS, width)

					Graph.astar(inDraw, grid, start, end)

					#Graph.dijkstra(inDraw, grid, start, end)
					
					toc = time.perf_counter()
					print(f"Solved in {toc - tic:0.4f} seconds")

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = Graph.setGrid(ROWS, width)

	pygame.quit()

main(WIN, WIDTH)