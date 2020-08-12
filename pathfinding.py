import pygame
import math
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
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Node:
	def __init__(self, row, col, wid, total_rows):
		self.row = row
		self.col = col
		self.wid = wid
		self.x = row * wid
		self.y = col * wid
		self.color = WHITE
		self.neighbour = []
		self.total_rows = total_rows

	#	Change these colours later for the sake of aesthetics

	def getPos(self):
		return self.row, self.col

	def isClosed(self):
		return self.color == RED

	def isOpen(self):
		return self.color == GREEN

	def isWall(self):
		return self.color == BLACK

	def isStart(self):
		return self.color == ORANGE

	def isEnd(self):
		return self.color == TURQUOISE

	def reset(self):
		return self.color == WHITE

	def setStart(self):
		self.color = ORANGE

	def setClosed(self):
		self.color = RED

	def setOpen(self):
		self.color = GREEN

	def setWall(self):
		self.color = BLACK

	def setEnd(self):
		self.color = TURQUOISE

	def setPath(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.wid, self.wid))

	def updateNeighbour(self, grid):
		pass

	#	Move further down later

	def __lt__(self, other):
		return False

def heuristic(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)

def setGrid(rows, wid):
	grid = []
	gap = wid // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			node = Node(i, j, gap, rows)
			grid[i].append(node)
	return grid

def drawGrid(win, rows, wid):
	GAP = wid // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (wid, i * gap))
		for j in range(rows):
			pygame.line(win, GREY, (j * gap, 0), (j * gap, wid))

def draw(win, grid, rows, wid):
	win.fill(WHITE)
	for row in grid:
		for node in row:
			node.draw(wid)
	drawGrid(win, rows, wid)
	pygame.display.update()

def getCLickPos(pos, rows, wid):
	gap = wid // rows
	y, x = pos
	row = y // gap
	col = x // gap
	return row, col

def main(win, wid):
	ROWS = 60	#	Change number according to how much you want
	grid = setGrid(ROWS, wid)
	start = None
	end = None
	run = True
	started = False
	while run:
		draw(win, grid, ROWS, wid)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if started:
				continue

			if pygame.mouse.get_pressed()[0]:	# 0 == left
				pos = pygame.mouse.getPos
				row, col = getCLickPos(pos, ROWS, wid)
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
				pos = pygame.mouse.getPos()
				row, col = getCLickPos(pos, ROWS, wid)
				node = grid[row][col]
				node.reset()
				if node == start:
					start = None
				elif node == end:
					end = None

			#if event.type == pygame.KEYDOWN:


	pygame.quit()

main(WIN, WIDTH)