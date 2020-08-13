import pygame
import math
import menu
import time
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Algorithms")

#	Change values of colours later to make it look better

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (54, 54, 54)
TURQUOISE = (64, 224, 208)
Blueish = (1, 255, 255)
Mintish = (1, 255, 195)
Pinkish = (255, 179, 253)
Purpleish = (157, 114, 255)
Greyish = (192, 192, 192)


class Node:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.width = width
		self.x = row * width
		self.y = col * width
		self.color = Greyish
		self.neighbour = []
		self.total_rows = total_rows

	#	Change these colours later for the sake of aesthetics

	def getPos(self):
		return self.row, self.col

	def isClosed(self):
		return self.color == Pinkish

	def isOpen(self):
		return self.color == Blueish

	def isWall(self):
		return self.color == BLACK

	def isStart(self):
		return self.color == Mintish

	def isEnd(self):
		return self.color == Purpleish

	def reset(self):
		return self.color == Greyish

	def setStart(self):
		self.color = Mintish

	def setEnd(self):
		self.color = Purpleish

	def setClosed(self):
		self.color = Pinkish

	def setOpen(self):
		self.color = Blueish

	def setWall(self):
		self.color = BLACK

	def setPath(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def updateNeighbour(self, grid):
		self.neighbour = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isWall():	#	D
			self.neighbour.append(grid[self.row + 1][self.col])
		
		if self.row > 0 and not grid[self.row - 1][self.col].isWall():						#	U
			self.neighbour.append(grid[self.row - 1][self.col])
		
		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isWall():	#	L
			self.neighbour.append(grid[self.row][self.col + 1])
		
		if self.col > 0 and not grid[self.row][self.col - 1].isWall():						#	R
			self.neighbour.append(grid[self.row][self.col - 1])

	#	Move further down later

	def __lt__(self, other):
		return False

def heuristic(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)

def astar(draw, grid, start, end):
	count = 0
	openSet = PriorityQueue()
	openSet.put((0, count, start))
	cameFrom = {}
	gScore = {node: float("inf") for row in grid for node in row}
	gScore[start] = 0
	fScore = {node: float("inf") for row in grid for node in row}
	fScore[start] = heuristic(start.getPos(), end.getPos())
	openSetHash = {start}

	while not openSet.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		curr = openSet.get()[2]
		openSetHash.remove(curr)

		if curr == end:
			constructPath(cameFrom, end, draw)
			end.setEnd()
			return True

		for n in curr.neighbour:
			tempgScore = gScore[curr] + 1
			if tempgScore < gScore[n]:
				cameFrom[n] = curr
				gScore[n] = tempgScore
				fScore[n] = tempgScore + heuristic(n.getPos(), end.getPos())
				if n not in openSetHash:
					count += 1
					openSet.put((fScore[n], count, n))
					openSetHash.add(n)
					n.setOpen()
		draw()
		if curr != start:
			curr.setClosed()
	return False

def dijkstra(draw, grid, start, end):
	pass

def constructPath(cameFrom, curr, draw):
	while curr in cameFrom:
		curr = cameFrom[curr]
		curr.setPath()
		draw()

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
		pygame.draw.line(win, WHITE, (0, i * gap), (width, i * gap))
		pygame.draw.line(win, WHITE, (i * gap, 0), (i * gap, width))

def draw(win, grid, rows, width):
	win.fill(WHITE)
	for row in grid:
		for node in row:
			node.draw(win)
	drawGrid(win, rows, width)
	pygame.display.update()

def getCLickPos(pos, rows, width):
	gap = width // rows
	y, x = pos
	row = y // gap
	col = x // gap
	return row, col

def main(win, width):
	ROWS = 50	#	Change number according to how much you want
	grid = setGrid(ROWS, width)
	start = None
	end = None
	run = True
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]:	# 0 == left
				pos = pygame.mouse.get_pos()
				row, col = getCLickPos(pos, ROWS, width)
				node = grid[row][col]
				if not start and node != end:
					start = node
					start.setStart()
				elif not end and node != start:
					end = node
					end.setEnd()
				elif node != end and node != start:
					node.setWall()

			elif pygame.mouse.get_pressed()[2]:	# 2 == right
				pos = pygame.mouse.get_pos()
				row, col = getCLickPos(pos, ROWS, width)
				node = grid[row][col]
				node.reset()
				if node == start:
					node.color = Greyish
					start = None
				elif node == end:
					node.color = Greyish
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame. K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.updateNeighbour(grid)

					astar(lambda: draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = setGrid(ROWS, width)

	pygame.quit()

main(WIN, WIDTH)