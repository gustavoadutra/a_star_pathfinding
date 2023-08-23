import pygame
from queue import PriorityQueue

WIDTH = 400
WIN = pygame.display.set_mode((WIDTH, WIDTH))

pygame.display.set_caption("A* Path Findind Algoritm")

# COLORS
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
    def __init__(self, row, col, width, total_rows):
        # numbers of lines and columns
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col
    
    def is_close(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == PURPLE
    
    def reset(self):
        return self.color == WHITE
    
    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_start(self):
        self.color = ORANGE

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    # draw in the desired grid with the desired color
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    # check where the algoritm can go
    def update_neighbors(self, grid):
        self.neighbors = []
        # check if the row not passed the limit of the window
        # and verify if there is a barrier in that place
        # if its true add to the neighbors list
        # down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): 
            self.neighbors.append(grid[self.row + 1][self.col])
        # up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): 
            self.neighbors.append(grid[self.row - 1][self.col])
        # right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): 
            self.neighbors.append(grid[self.row][self.col + 1])
        # left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): 
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False
    

# heuristic manhattan function 
def h(p1, p2):
    # receiveis point one and point 2
    # returns an sum of the distance between the end and the actual position
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0

    open_set = PriorityQueue()

    open_set.put((0, count, start))

    # keep track from where the node came from
    came_from = {}
    # sets the scores for each node to infinity
    g_score = {node: float("inf") for row in grid for node in row}
    f_score = {node: float("inf") for row in grid for node in row}
    # g distance is the shortest distance to the next node
    # how many nodes did the algoritm walk to arrive here
    g_score[start] = 0
    # to estimate how far is the end node 
    f_score[start] = h(start.get_pos(), end.get_pos())
    # to check witch value are in the queue
    open_set_hash = {start}

    while not open_set.empty():
        # quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        # get the current position
        current = open_set.get()[2]
        # remove the current position from the queue
        open_set_hash.remove(current)

        # if get to the end then reconstruct the path
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        # consider each neighbor
        for neighbor in current.neighbors:
            # the costs to move to another node is one
            temp_g_score = g_score[current] + 1

            # if the g_score of the neighbor is higher than the current go there
            # update this path and keep track of that
            # the only way to not happen this is finding an barrier
            if temp_g_score < g_score[neighbor]:
                # saves the current
                came_from[neighbor] = current
                # makes available to explore the neighbor
                # if not the neighbor g_score will continue to be infinity positive
                g_score[neighbor] = temp_g_score

                # calculates the estimative of the neighbor node is from the end
                # and sets this to f_score dictionary
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                # verify if th
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    # saves the locations where the node has been gone
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        # closes the paths where the alorithm already beem there
        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    grid = []
    # calculate the gap in the grid with an integer division between the width and the rows
    gap = width // rows
    # for each row
    # add an empty list to the grid
    # for each row
    for i in range(rows):
        grid.append([])
        # for each colunm
        for j in range(rows):
            node = Node(i, j, gap, rows)
            # add the node to the grid i position
            grid[i].append(node)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    # draw horizontal lines
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        # draw vertical lines
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


# draw white in the gaps
def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


# return the row and the column where the clcked happened
def get_clicked_pos(pos, rows, witdh):
    gap = witdh // rows
    y, x = pos
    # how many gaps do i need to get that column or row
    row = y // gap
    col = x // gap
    return row, col

def main(win, width):

    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(win, grid, ROWS, width)
        # to exit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # left mouse button
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                # draw the starts, ends and the barriers
                if not start and node != end:
                    start = node
                    start.make_start()
                
                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != end and node != start:
                    node.make_barrier()

            # right mouse button
            # reset the gap clicked
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            # starts the events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    # calls the algoritm
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                # clean the display
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)