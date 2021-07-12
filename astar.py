import pygame
from pygame.locals import *
pygame.init()
import math
from queue import PriorityQueue
import random
WIDTH = 800
screen = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("DEFENDER")

font = pygame.font.SysFont('Constantia', 30)
font1 = pygame.font.Font('freesansbold.ttf', 50)
font2 = pygame.font.Font('freesansbold.ttf', 20)
R = (0, 255, 141)
G = (0, 0, 0)
B = (0, 255, 0)
Y = (255, 255, 0)
W = (255, 255, 255)
Bl = (115, 134, 140)
P = (0, 191 , 255)
O = (255, 165 ,0)
Gr = (128, 128, 128)
T = (64, 224, 208)
#global b
AI =1
level = 4


class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = W
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
## here we are defining every block type with individual color so that we can identify them
	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == R

	def is_open(self):
		return self.color == G

	def is_barrier(self):
		return self.color == Bl

	def is_start(self):
		return self.color == O

	def is_end(self):
		return self.color == T

	def reset(self):
		self.color = W

	def make_start(self):
		self.color = O

	def make_closed(self):
		self.color = R

	def make_open(self):
		self.color = G

	def make_barrier(self):
		self.color = Bl

	def make_end(self):
		self.color = T

	def make_path(self):
		self.color = P

	def draw(self, screen):
		pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN SPOT IS OUT OF BOX AND NOT BARRIER
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UPPER SPOT IS OUT OF BOX AND NOT BARRIER
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT SPOT IS OUT OF BOX AND NOT BARRIER
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT  IS OUT OF BOX AND NOT BARRIER
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False

	
# WITH 	MAKE GRID WE ARE KEEPING AN 2D ARRAY FOR REPRESENTING THE BOARD

def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid
# THEN WE DRAW THE BOARD WITH PYGAME 
def draw_grid(screen, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(screen, Gr, (0, i * gap), (width, i * gap)) # HERE WE DRAW THE HORIZONTAL LINE
		for j in range(rows):
			pygame.draw.line(screen, Gr, (j * gap, 0), (j * gap, width)) # VERTICAL LINE
###########################################################################


# IT WILL GIVE THE WHOLE BOARD A FILL BACKGROUND. IT NEEDS TO RUN BEGINNING OF EVERY FRAME . 
#EVERY UPDATE ON UI WE NEED TO RUN THIS SO THAT THE THINGS PREVIOUSLY ON IT COMES BACK

def draw(screen, grid, rows, width):
	screen.fill(W)

	for row in grid:
		for spot in row:
			spot.draw(screen)

	draw_grid(screen, rows, width)
	pygame.display.update()  # IT UPDATES EVERYTHING EVERYTIME WE CLICK ON THE SCREEN

##########################################################################

def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, end):

	global AI
	count = 1
	
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row} # INITIALLY g_score SET TO ZERO
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row} # INITIALLY f_score IS SET TO HEURISTIC VALUE
	f_score[start] = h(start.get_pos(), end.get_pos()) # HEURISTIC VALUE IS DEFINED BY DISTANCE BETWEEN THEM CALCULATED FROM h funciton

	open_set_hash = {start} 

	while not open_set.empty(): # WE NEED TO GO THROUGH EVERY SPOT FROM OPEN SET UNTIL ITS EMPTY AND IF OPEN_SET IS EMPTY AND WE DIDNT REACH OUR DESTINATION THATS MEASM PATH DOESNT EXIST
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2] # OPEN SET STORE F_SCORE,COUNT,NODE.SO WE NEED TO ACCESS 3RD ELEMENT
		open_set_hash.remove(current)

		if current == end: # IF WE FOUND THE SHORTEST PATH OR NOT
			#print(b)
			#print(count)
			global AI
			AI = count
			#print("AI",AI)
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1 # AS EVERY NEIGHBOUR IS ONE SPOT DIFFERENCE FROM ITSELF SO WE ADD 1 WITH g_socre

			if temp_g_score < g_score[neighbor]: #IF WE FOUND BETTER g_score than we found before
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				
				if neighbor not in open_set_hash: # just check if we already consider it
					count += 1
					#print(count)
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False

def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
 


def main(screen, width):  #### Display for main game screen
	ROWS = 25
	grid = make_grid(ROWS, width)

	start = None
	end = None
	block = 0
	run = True
	while run:
		draw(screen, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		
            
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end: # Press Space to start the turn of AI
					#print('block' ,block)
					dist = h(start.get_pos(), end.get_pos())
					#print('dist',dist)

					
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					algorithm(lambda: draw(screen, grid, ROWS, width), grid, start, end)
					#print('count',AI)
					player = (dist + block) * level
					if (AI < player):
                        #draw_text('START', font, (255,0 ,0 ), screen, 340, 350)
                        #pygame.display.set_caption("DEFENDasER")
						print('AI win')
					else:
						print('YOU WIN')
				

				if event.key == pygame.K_BACKSPACE:
					start = None
					end = None
					grid = make_grid(ROWS, width)
					count = 0
					block = 0
					dist = 0
                    #run = False
				
				elif event.key == pygame.K_TAB:
					start = grid[random.randrange(0,24)][random.randrange(0,24)]
					start.make_start()

					end = grid[random.randrange(0,24)][random.randrange(0,24)]
					while(start == end):
						end = grid[random.randrange(0,24)][random.randrange(0,24)]	
					end.make_end()



			if pygame.mouse.get_pressed()[0]: # LEFT mouse button action
			
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				#print(row)
				#print(col)
				#print(grid[row][col])
				spot = grid[row][col]
				#print(type(spot))
				


				if spot != end and spot != start:
					if spot.is_barrier() != True : # Check so that if one spot is clicked double time shouldn't consider it 
						#print(spot.row,spot.col , barri)
						spot.make_barrier()
						block = block + 1



            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_ESCAPE:
            #         print('f')  
			# elif pygame.mouse.get_pressed()[1]: # RIGHT button pressed to reset the game and start another round
				
			# 	pos = pygame.mouse.get_pos()
			# 	row, col = get_clicked_pos(pos, ROWS, width)
			# 	spot = grid[row][col]
			# 	spot.reset()
		
			# 	start = None
				
			# 	end = None
			# 	#count = 0
			# 	block = 0
			# 	dist=0
			# 	for row in grid:
			# 		for spot in row:
			# 			spot.reset()
				
			# 	continue
    

	pygame.quit()


click = False

def main_menu(): ###### landing page


    while True:
 
        screen.fill((102,178,155))
     
 
        mx, my = pygame.mouse.get_pos()
 
        button_1 = pygame.Rect(300, 350, 200, 50)
        
        
        
        if button_1.collidepoint((mx, my)):
            if click:
                main(screen,WIDTH)
        
        pygame.draw.rect(screen, (255, 255, 255), button_1)
        draw_text('Defender', font1, (0,0 ,0 ), screen, 300, 200)
        draw_text('START', font, (0,0 ,0 ), screen, 350, 360)
        draw_text('How to Play', font, (0,0 ,0 ), screen, 250, 470)
        draw_text('Press Tab for random souce and destination ', font2, (0,0 ,0 ), screen, 250, 530)
        draw_text('Left mouse button to put obstacle', font2, (0,0 ,0 ), screen, 250, 570)
        draw_text('Space to start AI to play', font2, (0,0 ,0 ), screen, 250, 610)
        draw_text('Backspace to clear the screen', font2, (0,0 ,0 ), screen, 250, 650)

        
        

        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:# KEYBOARD
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN: #MOUSE
                if event.button == 1:
                    click = True
 
        pygame.display.update()
        #mainClock.tick(60)
 
# def game():
#     running = True
#     while running:
#         screen.fill((0,0,0))
        
    
#         for event in pygame.event.get():
#             if event.type == QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == KEYDOWN:
#                 if event.key == K_ESCAPE:
#                     running = False
        
#         pygame.display.update()
#         #mainClock.tick(60)
 

main_menu()
