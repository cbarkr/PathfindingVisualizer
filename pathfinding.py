import pygame
import pygame_menu
import math
import random
import time
from queue import PriorityQueue

#####	Window Setup	#####
WIDTH = 800
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption(" ")
WIN = pygame.display.set_mode((WIDTH, WIDTH))
windowFont = pygame.font.SysFont("Open Sans Light", 18)

#####	Colours	#####
white = (255, 255, 255)
grey = (192, 192, 192)
black = (0, 0, 0)
pink = (255, 179, 253)
mint = (1, 255, 195)
turqoise = (54, 158, 145)
blue = (1, 255, 255)
lightBlue = (25, 151, 201)
darkBlue = (12, 46, 82)
purple1 = (128, 0, 128)
purple2 = (157, 114, 255)

#####	Menu Setup	#####
selectedAlgorithm = 0	#	A* by default
barrierPercent = 0		#	0% randomly generated barrier by default

themeFont = pygame_menu.font.FONT_OPEN_SANS_LIGHT
myTheme = pygame_menu.themes.Theme(
	widget_font = themeFont,
	title_font_color = white,
	title_background_color = turqoise,
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
instructionsMenu = pygame_menu.Menu(WIDTH, WIDTH, theme = myTheme, title = "Instructions")
endMenu = pygame_menu.Menu(WIDTH, WIDTH, theme = myTheme, title = "End")

mainMenu.add_selector('Algorithm: ', [('A*', 1), ('Dijkstra', 2), ('BFS', 3)], onchange = selectAlgorithm)
mainMenu.add_selector('Random Barrier %: ', [('0%', 1), ('10%', 2), ('20%', 3), ('30%', 4), ('40%', 5),
											('50%', 6), ('60%', 7), ('70%', 8), ('80%', 9), ('90%', 10)],
											onchange = randomBarrierPercent)
mainMenu.add_button('Start', startPathfinding)
mainMenu.add_button(instructionsMenu.get_title(), instructionsMenu)
mainMenu.add_button('Exit', pygame_menu.events.EXIT)

instructions1 	= "LEFT MOUSE: set nodes"
instructions2 	= "- click 1: set start"
instructions3 	= "- click 2: set end"
instructions4 	= "- click 3+: set barrier"
instructions5 	= "RIGHT MOUSE: remove nodes "
instructions6 	= "SPACE KEY: start pathfinding"
instructions7 	= "C KEY: clear the board"
instructions8 	= "Q KEY: quit"
instructions9 	= "R KEY: display results"
instructions10 	= "ESC KEY: open the menu"

instructionsMenu.add_button('Return', pygame_menu.events.RESET)
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

#####	Node Class 	#####
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
		return self.row, self.col 		#	Return node position (x, y)

	def isClosed(self):
		return self.color == pink 		#	If node has been traversed

	def isOpen(self):
		return self.color == blue 		# 	If node is a neighbour

	def isWall(self):
		return self.color == black		#	If node is a barrier

	def isStart(self):
		return self.color == mint		#	If node is start node

	def isEnd(self):
		return self.color == purple2	#	If node is end node

	def reset(self):
		return self.color == grey		#	Reset a node to default

	def setStart(self):
		self.color = mint		#	Set node as start node

	def setEnd(self):
		self.color = purple2	#	Set node as end node

	def setClosed(self):
		self.color = pink 		#	Set node as traversed

	def setOpen(self):
		self.color = blue 		# 	Set node as neighbour

	def setWall(self):
		self.color = black		#	Set node as barrier 

	def setPath(self):
		self.color = purple1	#	Set node as part of shortest path

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))			#	Draw path

	def updateNeighbour(self, grid):
		self.neighbour = []

		if self.row > 0 and not grid[self.row - 1][self.col].isWall():						#	Neighbour node is north
			self.neighbour.append(grid[self.row - 1][self.col])

		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isWall():	#	Neighbour node is south
			self.neighbour.append(grid[self.row + 1][self.col])
		
		if self.col > 0 and not grid[self.row][self.col - 1].isWall():						#	Neighbour node is east
			self.neighbour.append(grid[self.row][self.col - 1])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isWall():	#	Neighbour node is west
			self.neighbour.append(grid[self.row][self.col + 1])

	def __lt__(self, other):
		return False

nodeCount = 0	#	Count number of nodes in shortest path

#####	Graph Class    #####
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
		gap = width // rows 												#	Gap between lines in grid
		for i in range(rows):
			pygame.draw.line(win, white, (0, i * gap), (width, i * gap))	#	Draw horizontal grid lines
			pygame.draw.line(win, white, (i * gap, 0), (i * gap, width))	#	Draw vertical grid lines

	def drawRandomBarrier(grid, rows, randomBarrierAmount):
		node = None
		for i in range(randomBarrierAmount):
			randomX = random.randrange(rows)	#	Obtain random x value in row
			randomY = random.randrange(rows)	#	Obtain random y value in column
			node = grid[randomX][randomY]		#	Set node to random (x, y) coordinate
			node.setWall()						#	Set random node as barrier

	def draw(win, grid, rows, width):
		win.fill(white)
		for row in grid:
			for node in row:
				node.draw(win)
		Graph.drawGrid(win, rows, width)		#	Draw grid in pygame window
		pygame.display.update()					#	Draw pygame window on user display

	def getCLickPos(pos, rows, width):
		gap = width // rows 					#	Gap between lines in grid
		y, x = pos 								
		row = y // gap
		col = x // gap
		return row, col

	def heuristic(point1, point2):				#	Return Manhattan distance
		x1, y1 = point1
		x2, y2 = point2
		return abs(x1 - x2) + abs(y1 - y2)


	#####	Pathfinding Algorithms 	 #####
	def astar(draw, grid, start, end):
		untraversedSet = PriorityQueue()		#	Untraversed nodes
		untraversedSet.put((0, start))

		traversedSet = {start}					#	Traversed nodes

		cameFrom = {}							#	Previous nodes

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

		while not untraversedSet.empty():			#	Iterate through untraversed nodes
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			currentNode = untraversedSet.get()[1]	#	Retrieve node from set
			traversedSet.remove(currentNode)		#	Keep track of traversed nodes by removing from other set

			if currentNode == end:
				Graph.constructPath(cameFrom, end, draw)	#	Draw path from list of nodes gathered
				end.setEnd()	
				return True 	#	Path found

			for node in currentNode.neighbour:
				newCost = currentCost[currentNode] + 1		#	New cost is greater than current cost at current node

				if newCost < currentCost[node]:				#	Check new cost against the cost of the neighbouring node
					cameFrom[node] = currentNode
					currentCost[node] = newCost
					priorityCost[node] = newCost + Graph.heuristic(node.getPos(), end.getPos())	#	Prioritize cost of Manhattan distance between neighbour and end

					if node not in traversedSet:			#	Checking nodes that have not been traversed
						untraversedSet.put((priorityCost[node], node))
						traversedSet.add(node)
						node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		return False	#	Path not found

	def dijkstra(draw, grid, start, end):	#	Basically A* but without heuristic
		untraversedSet = PriorityQueue()	#	Untraversed nodes
		untraversedSet.put((0, start))

		traversedSet = {start}				#	Traversed nodes

		cameFrom = {}						#	Previous nodes

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

		while not untraversedSet.empty():			#	Iterate through untraversed nodes
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()

			currentNode = untraversedSet.get()[1]	#	Retrieve node from set
			traversedSet.remove(currentNode)		#	Keep track of traversed nodes by removing from other set

			if currentNode == end:
				Graph.constructPath(cameFrom, end, draw)	#	Draw path from list of nodes gathered
				end.setEnd()
				return True 	#	Path found

			for node in currentNode.neighbour:
				newCost = currentCost[currentNode] + 1		#	New cost is greater than current cost at current node

				if newCost < currentCost[node]:				#	Check new cost against the cost of the neighbouring node
					cameFrom[node] = currentNode
					currentCost[node] = newCost
					priorityCost[node] = newCost 

					if node not in traversedSet:			#	Checking nodes that have not been traversed
						untraversedSet.put((priorityCost[node], node))
						traversedSet.add(node)
						node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		return False	#	Path not found

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
				return True 	#	Path found

			for node in currentNode.neighbour:
				if node not in traversedSet:	#	Checking nodes that have not been traversed
					cameFrom[node] = currentNode
					traversedSet.append(node)
					untraversedSet.append(node)
					node.setOpen()

			draw()

			if currentNode != start:
				currentNode.setClosed()

		return False	#	Path not found

#####	Main 	#####
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

			if pygame.mouse.get_pressed()[0]:						#	0 == left mouse
				pos = pygame.mouse.get_pos()
				row, col = Graph.getCLickPos(pos, ROWS, width)
				node = grid[row][col]
				if not start and node != end:
					start = node
					start.setStart()				#	First click sets start node
				elif not end and node != start:
					end = node
					end.setEnd()					#	Second click set start node
				elif node != end and node != start:
					node.setWall()					#	Subsequent clicks set barrier nodes

			elif pygame.mouse.get_pressed()[2]:						#	2 == right mouse
				pos = pygame.mouse.get_pos()
				row, col = Graph.getCLickPos(pos, ROWS, width)
				node = grid[row][col]
				node.reset()
				if node == start:
					node.color = grey		#	Delete start node and select new one
					start = None
				elif node == end:
					node.color = grey		#	Delete end node and select new one
					end = None
				elif node.isWall():
					node.color = grey		#	Delete barrier nodes and select new ones

			if event.type == pygame.KEYDOWN:
				if event.key == pygame. K_SPACE and start and end:	#	Space starts pathfinding
					for row in grid:
						for spot in row:
							spot.updateNeighbour(grid)

					tic = time.perf_counter()						#	Timer start

					inDraw = lambda: Graph.draw(win, grid, ROWS, width)

					if selectedAlgorithm == 0:						#	Option 0 == A*
						Graph.astar(inDraw, grid, start, end)

					elif selectedAlgorithm == 1:					#	Option 1 == Dijkstra
						Graph.dijkstra(inDraw, grid, start, end)

					elif selectedAlgorithm == 2:					#	Option 2 == BFS
						Graph.bfs(inDraw, grid, start, end)
					
					toc = time.perf_counter()						#	Timer end
					timer = (toc - tic)

					#print(f"Solved in {timer:0.4f} seconds")		#	Optionally print results


				if event.key == pygame.K_r:							#	Results shortcut
					endMenu.add_label('Solved in ' + '{:0.4f}'.format(timer) + ' seconds', font_size = 20)
					if nodeCount > 0:
						endMenu.add_label('Path is ' + str(nodeCount) + ' nodes long', font_size = 20)

					else:
						endMenu.add_label('Path not found', font_size = 20)

					endMenu.mainloop(win)

				if event.key == pygame.K_c:							#	Clear shortcut
					start = None
					end = None
					grid = Graph.setGrid(ROWS, width)				# 	Reset grid

					if barrierPercent != 0:
						Graph.drawRandomBarrier(grid, ROWS, randomBarrierAmount)

				if event.key == pygame.K_q:							#	Quit shortcut
					run = False
					pygame.QUIT

				if event.key == pygame.K_ESCAPE:
					mainMenu.mainloop(WIN)

	pygame.quit()

mainMenu.mainloop(WIN)