import pygame
import pygame_menu
import math
import random
import time
from queue import PriorityQueue

"""
Window Setup
"""
WIDTH = 800
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption(" ")
WIN = pygame.display.set_mode((WIDTH, WIDTH))
windowFont = pygame.font.SysFont("Open Sans Light", 18)

"""
Colours
"""
white = (255, 255, 255)
grey = (192, 192, 192)
black = (0, 0, 0)

pink = (255, 179, 253)
mint = (1, 255, 195)
turqoise1 = (93, 192, 172)
turqoise2 = (54, 158, 145)
blue = (1, 255, 255)
lightBlue = (25, 151, 201)
darkBlue = (12, 46, 82)
purple1 = (128, 0, 128)
purple2 = (157, 114, 255)

"""
Menu Setup
"""
selectedAlgorithm = 0	#	Set to A* by default
barrierPercent = 0	#	Set to 0% randomly generated barrier by default

themeFont = pygame_menu.font.FONT_OPEN_SANS_LIGHT
#myTheme = pygame_menu.themes.THEME_DARK.copy()
myTheme = pygame_menu.themes.Theme(
	widget_font = themeFont,
	title_font_color = white,
	title_background_color = turqoise2,
	widget_background_color = grey,
	widget_font_color = black,
	background_color = grey,
	focus_background_color = (1, 255, 255, 157),
	title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE,
	selection_color = black,
	menubar_close_button = False)

def selectAlgorithm(inAlgorithm, index):
	global selectedAlgorithm
	selectedAlgorithm = inAlgorithm[1]
	return selectedAlgorithm

def randomBarrierPercent(displayPercent, index):
	global barrierPercent
	barrierPercent = (index - 1) * 10
	return barrierPercent

def startPathfinding():
	main(WIN, WIDTH, selectedAlgorithm, barrierPercent)

mainMenu = pygame_menu.Menu(WIDTH, WIDTH, theme = myTheme, title = "Pathfinding Visualizer")
instructionsMenu = pygame_menu.Menu(WIDTH, WIDTH, theme = myTheme, title = "Instructions", column_force_fit_text = True)
endMenu = pygame_menu.Menu(WIDTH, WIDTH, theme = myTheme, title = "End", column_force_fit_text = True)

mainMenu.add_selector('Algorithm: ', [('A*', 1), ('Dijkstra', 2), ('BFS', 3)], onchange = selectAlgorithm)
mainMenu.add_selector('Random Barrier %: ', [('0%', 1), ('10%', 2), ('20%', 3), ('30%', 4), ('40%', 5), ('50%', 6), ('60%', 7), ('70%', 8), ('80%', 9), ('90%', 10)], onchange = randomBarrierPercent)
mainMenu.add_button('Start', startPathfinding)
mainMenu.add_button(instructionsMenu.get_title(), instructionsMenu)
mainMenu.add_button('Exit', pygame_menu.events.EXIT)

instructions1 = "LEFT MOUSE: set nodes"
instructions2 = "- click 1: set start"
instructions3 = "- click 2: set end"
instructions4 = "- click >2: set barrier"
instructions5 = "RIGHT MOUSE: remove nodes "
instructions6 = "SPACE KEY: start pathfinding"
instructions7 = "C KEY: clear the board"
instructions8 = "Q KEY: quit"
instructions9 = "R KEY: display results"
instructions10 = "ESC KEY: open the menu"

instructionsMenu.add_button('Return', mainMenu)
instructionsMenu.add_label(instructions1, font_size = 20)
instructionsMenu.add_label(instructions2, font_size = 20)
instructionsMenu.add_label(instructions3, font_size = 20)
instructionsMenu.add_label(instructions4, font_size = 20)
instructionsMenu.add_label(instructions5, font_size = 20)
instructionsMenu.add_label(instructions6, font_size = 20)
instructionsMenu.add_label(instructions7, font_size = 20)
instructionsMenu.add_label(instructions8, font_size = 20)
instructionsMenu.add_label(instructions9, font_size = 20)
instructionsMenu.add_label(instructions10, font_size = 20)

endMenu.add_button('Return', mainMenu)

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
nodeCount = 0
class Graph:
	def constructPath(cameFrom, curr, draw):
		global nodeCount
		while curr in cameFrom:
			nodeCount += 1
			curr = cameFrom[curr]
			curr.setPath()
			draw()
		#print("Path is " + str(nodeCount) + " nodes long")	#	Optionally print results

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

	def drawRandomBarrier(grid, rows, randomBarrierAmount):
		node = None
		for i in range(randomBarrierAmount):
			randomx = random.randrange(rows)	#	Obtain random x value in row
			randomy = random.randrange(rows)	#	Obtain random y value in column
			node = grid[randomx][randomy]
			node.setWall()	#	Set random node as barrier

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

		while not untraversedSet.empty():	#	Iterate through untraversed nodes
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			currentNode = untraversedSet.get()[1]	#	Retrieve node from set
			traversedSet.remove(currentNode)	#	Keep track of traversed nodes by removing from other set

			if currentNode == end:
				Graph.constructPath(cameFrom, end, draw)	#	Draw path from list of nodes gathered
				end.setEnd()	
				return True

			for node in currentNode.neighbour:
				newCost = currentCost[currentNode] + 1	#	New cost is greater than current cost at current node

				if newCost < currentCost[node]:	#	Check new cost against the cost of the neighbouring node
					cameFrom[node] = currentNode
					currentCost[node] = newCost
					priorityCost[node] = newCost + Graph.heuristic(node.getPos(), end.getPos())	#	Prioritize cost of Manhattan distance between neighbour and end

					if node not in traversedSet:	#	Checking nodes that have not been traversed
						untraversedSet.put((priorityCost[node], node))
						traversedSet.add(node)
						node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		#print("Path not found")	#	Optionally print results
		return False

	def dijkstra(draw, grid, start, end):	#	Basically A* but without heuristic
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

		while not untraversedSet.empty():	#	Iterate through untraversed nodes
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			currentNode = untraversedSet.get()[1]	#	Retrieve node from set
			traversedSet.remove(currentNode)	#	Keep track of traversed nodes by removing from other set

			if currentNode == end:
				Graph.constructPath(cameFrom, end, draw)	#	Draw path from list of nodes gathered
				end.setEnd()
				return True

			for node in currentNode.neighbour:
				newCost = currentCost[currentNode] + 1	#	New cost is greater than current cost at current node

				if newCost < currentCost[node]:	#	Check new cost against the cost of the neighbouring node
					cameFrom[node] = currentNode
					currentCost[node] = newCost
					priorityCost[node] = newCost

					if node not in traversedSet:	#	Checking nodes that have not been traversed
						untraversedSet.put((priorityCost[node], node))
						traversedSet.add(node)
						node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		#print("Path not found")	#	Optionally print results
		return False

	def bfs(draw, grid, start, end):
		untraversedSet = []
		traversedSet = []
		cameFrom = {}

		untraversedSet.append(start)
		traversedSet.append(start)

		while untraversedSet:	#	Iterate through untraversed nodes
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			currentNode = untraversedSet.pop(0)	#	Starts at start node

			if currentNode == end:
				Graph.constructPath(cameFrom, end, draw)	#	Draw path from list of nodes gathered
				end.setEnd()
				return True

			for node in currentNode.neighbour:
				if node not in traversedSet:	#	Checking nodes that have not been traversed
					cameFrom[node] = currentNode
					traversedSet.append(node)
					untraversedSet.append(node)
					node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		#print("Path not found")	#	Optionally print results
		return False

"""
Main
"""
def main(win, width, selectedAlgorithm, barrierPercent):
	ROWS = 50
	grid = Graph.setGrid(ROWS, width)
	start = None
	end = None
	randomBarrierAmount = int((barrierPercent / 100) * (ROWS * ROWS))
	run = True
	global timer

	if barrierPercent != 0:
			Graph.drawRandomBarrier(grid, ROWS, randomBarrierAmount)

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
				if node == start:	#	Delete start node and select new one
					node.color = grey
					start = None
				elif node == end:	#	Delete end node and select new one
					node.color = grey
					end = None
				elif node.isWall():	#	Delete barrier nodes and select new ones
					node.color = grey

			if event.type == pygame.KEYDOWN:
				if event.key == pygame. K_SPACE and start and end:	
					for row in grid:
						for spot in row:
							spot.updateNeighbour(grid)

					tic = time.perf_counter()	#	Timer start

					inDraw = lambda: Graph.draw(win, grid, ROWS, width)

					if selectedAlgorithm == 0:	#	0 == A*
						Graph.astar(inDraw, grid, start, end)

					elif selectedAlgorithm == 1:	#	1 == Dijkstra
						Graph.dijkstra(inDraw, grid, start, end)

					elif selectedAlgorithm == 2:	#	2 == BFS9
						Graph.bfs(inDraw, grid, start, end)
					
					toc = time.perf_counter()	#	Timer end
					timer = (toc - tic)

					#print(f"Solved in {timer:0.4f} seconds")	#	Optionally print results


				if event.key == pygame.K_r:	#	r == results shortcut
					endMenu.add_label('Solved in ' + '{:0.4f}'.format(timer) + ' seconds', font_size = 20)
					if nodeCount > 0:
						endMenu.add_label('Path is ' + str(nodeCount) + ' nodes long', font_size = 20)

					else:
						endMenu.add_label('Path not found', font_size = 20)

					endMenu.mainloop(win)

				if event.key == pygame.K_c:	#	c == clear shortcut
					start = None
					end = None
					grid = Graph.setGrid(ROWS, width)

					if barrierPercent != 0:
						Graph.drawRandomBarrier(grid, ROWS, randomBarrierAmount)

				if event.key == pygame.K_q:	#	q == quit shortcut
					run = False
					pygame.QUIT

				if event.key == pygame.K_ESCAPE:
					mainMenu.mainloop(WIN)

	pygame.quit()

mainMenu.mainloop(WIN)