import pygame
import pygame_menu
import math
import time
from queue import PriorityQueue

"""
Window Setup
"""
pygame.init()
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Algorithms")
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
selectedAlgorithm = 'A*'	#	Set to A* by default
randomizedBarrier = False
clock = pygame.time.Clock()

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
	selectedAlgorithm = inAlgorithm[0]
	return selectedAlgorithm

def startPathfinding():
	main(WIN, WIDTH, selectedAlgorithm)

mainMenu = pygame_menu.Menu(WIDTH, WIDTH, theme = myTheme, title = "Pathfinding Visualizer")
instructionsMenu = pygame_menu.Menu(WIDTH, WIDTH, theme = myTheme, title = "Instructions", column_force_fit_text = True)

mainMenu.add_selector('Algorithm: ', [('A*', 1), ('Dijkstra', 2), ('BFS (In progress!)', 3)], onchange=selectAlgorithm)
mainMenu.add_button('Start', startPathfinding)
mainMenu.add_button(instructionsMenu.get_title(), instructionsMenu)
mainMenu.add_button('Exit', pygame_menu.events.EXIT)

instructions1 = "LEFT MOUSE: set nodes"
instructions2 = "node 1 = start, node 2 = end, node >2 = barrier"
instructions3 = "RIGHT MOUSE: remove nodes "
instructions4 = "C KEY: clear the board"
instructions5 = "Q KEY: quit"
instructions6 = "Esc KEY: open the menu"

instructionsMenu.add_button('Return', pygame_menu.events.RESET)
instructionsMenu.add_label(instructions1, font_size = 20)
instructionsMenu.add_label(instructions2, font_size = 20)
instructionsMenu.add_label(instructions3, font_size = 20)
instructionsMenu.add_label(instructions4, font_size = 20)
instructionsMenu.add_label(instructions5, font_size = 20)
instructionsMenu.add_label(instructions6, font_size = 20)

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
		global nodeCount
		nodeCount = 0
		while curr in cameFrom:
			nodeCount += 1
			curr = cameFrom[curr]
			curr.setPath()
			draw()
		print("Path is " + str(nodeCount) + " nodes long")

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
			for node in row:
				currentCost[node] = float("inf")	#	Initially set every entry to infinity
		currentCost[start] = 0

		priorityCost = {}
		for row in grid:
			for node in row:
				priorityCost[node] = float("inf")	#	Initially set every entry to infinity
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

	def bfs(draw, grid, start, end):
		print("In progress!")
		untraversedSet = {}
		traversedSet = {start}

		cameFrom = {}

		while untraversedSet:

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			currentNode = untraversedSet.pop(0)

			if currentNode == end:
				Graph.constructPath(cameFrom, end, draw)
				end.setEnd()
				return True

			for node in currentNode.neighbour:
				cameFrom[node] = currentNode
				if currentNode.neighbour not in traversedSet:
					traversedSet.add(currentNode.neighbour)
					untraversedSet.append(currentNode.neighbour)
					node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		return False

"""
Main
"""
def main(win, width, selectedAlgorithm):
	ROWS = 50
	grid = Graph.setGrid(ROWS, width)
	start = None
	end = None
	run = True
	global timer

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

					if selectedAlgorithm == 'A*':
						Graph.astar(inDraw, grid, start, end)

					elif selectedAlgorithm == 'Dijkstra':
						Graph.dijkstra(inDraw, grid, start, end)

					elif selectedAlgorithm == 'BFS':
						Graph.bfs(inDraw, grid, start, end)
					
					toc = time.perf_counter()	#	Timer end
					timer = toc - tic

					print(f"Solved in {timer:0.4f} seconds")

				if event.key == pygame.K_c:	#	c == reset shortcut
					start = None
					end = None
					grid = Graph.setGrid(ROWS, width)

				if event.key == pygame.K_q:	#	q == quit shortcut
					run = False
					pygame.QUIT

				if event.key == pygame.K_ESCAPE:
					mainMenu.mainloop(WIN)

	pygame.quit()

"""	

	In progress!
	Hoping to display the time taken to find the shortest path and the amount of nodes in that path

	pygame.font.init()
	mainFont = pygame.font.SysFont('Arial', 50)
					
	timerLabel = mainFont.render(f"Time:  {timer}", True, black)
	nodeCountLabel = mainFont.render(f"Nodes: {nodeCount}", True, black)

	WIN.blit(timerLabel, (10, 10))
	WIN.blit(nodeCountLabel, (WIDTH - nodeCountLabel.get_width() - 10, 10))"""

mainMenu.mainloop(WIN)