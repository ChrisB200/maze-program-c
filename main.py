import pygame
from pygame.locals import *
import sys
import os
import ctypes
import scripts.user_interface as ui

def load_shared_library(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    return ctypes.CDLL(path)


WIDTH, HEIGHT = 1500, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

generator_lib = load_shared_library("lib/maze-generator.so")
solver_lib = load_shared_library("lib/maze-solver.so")
DIRECTIONS = {"TOP": 0, "RIGHT": 1, "BOTTOM": 2, "LEFT": 3}

DRAW_RECT = pygame.USEREVENT + 1


class Node(ctypes.Structure):
    pass


Node._fields_ = [
    ("vertex", ctypes.c_int),
    ("row", ctypes.c_int),
    ("col", ctypes.c_int),
    ("walls", ctypes.POINTER(ctypes.c_bool)),
    ("visited", ctypes.c_bool),
    ("searched", ctypes.c_bool),
    ("path", ctypes.c_bool),
    ("parent", ctypes.c_int),
    ("next", ctypes.POINTER(Node)),
]


class Maze(ctypes.Structure):
    _fields_ = [
        ("rows", ctypes.c_int),
        ("cols", ctypes.c_int),
        ("num_nodes", ctypes.c_int),
        ("nodes", ctypes.POINTER(ctypes.POINTER(Node))),
        ("size", ctypes.c_size_t),
    ]


class BfsInfo(ctypes.Structure):
    _fields_ = [
        ("max_size", ctypes.c_int),
        ("start", ctypes.c_int),
        ("end", ctypes.c_int),
        ("rear", ctypes.c_int),
        ("front", ctypes.c_int),
        ("solved", ctypes.c_bool),
        ("visited", ctypes.POINTER(ctypes.c_bool)),
        ("queue", ctypes.POINTER(ctypes.c_int)),
    ]


# function prototypes
generator_lib.generate_maze.argtypes = [ctypes.c_int, ctypes.c_int]
generator_lib.generate_maze.restype = ctypes.POINTER(Maze)

generator_lib.free_maze.argtypes = [ctypes.POINTER(Maze)]

generator_lib.print_graph.argtypes = [ctypes.POINTER(Maze)]

solver_lib.solve_maze.argtypes = [ctypes.POINTER(Maze)]

solver_lib.create_bfs_info.argtypes = [ctypes.POINTER(Maze), ctypes.c_int, ctypes.c_int]
solver_lib.create_bfs_info.restype = ctypes.POINTER(BfsInfo)

solver_lib.free_bfs_info.argtypes = [ctypes.POINTER(BfsInfo)]

solver_lib.shortest_path.argtypes = [ctypes.POINTER(Maze)]

solver_lib.bfs_step.argtypes = [ctypes.POINTER(Maze), ctypes.POINTER(BfsInfo)]
solver_lib.bfs_step.restypes = ctypes.c_int


class Grid:
    def __init__(
        self,
        rows,
        cols,
        node_size,
        line_size,
        bg_colour=(255, 255, 255),
        line_colour=(0, 0, 0),
    ):
        self.transform = pygame.math.Vector2()
        self.rows = rows
        self.cols = cols
        self.node_size = node_size
        self.line_size = line_size
        self.bg_color = bg_colour
        self.line_color = line_colour

        # c maze info
        self.maze = None
        self.bfs_info = None

        # cells
        self.maze_surf = pygame.Surface(self.get_size())
        self.maze_cells = []
        self.isSolving = False
        self.speed = 1

        # movement
        self.zoom = 1
        self.zoom_increment = 0
        self.mousePositions = []
        self.isDragging = False

        self.get_maze()

    @property
    def image(self):
        return pygame.transform.scale(
            self.maze_surf,
            (
                self.get_width() + self.zoom_increment,
                self.get_height() + self.zoom_increment,
            ),
        )

    def cell_width(self):
        return self.node_size[0] + self.zoom_increment

    def cell_height(self):
        return self.node_size[1] + self.zoom_increment

    def get_width(self):
        return (self.node_size[0] * self.cols) + self.line_size

    def get_height(self):
        return (self.node_size[1] * self.rows) + self.line_size

    def get_size(self):
        return self.get_width(), self.get_height()

    def rect(self):
        return pygame.Rect(
            self.transform.x,
            self.transform.y,
            self.get_width() * self.zoom,
            self.get_height() * self.zoom,
        )

    def event_handler(self, event):
        if event.type == DRAW_RECT:
            self.bfs_step()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.math.Vector2(pygame.mouse.get_pos())
            if event.button == 1 and self.rect().collidepoint(mouse):
                self.isDragging = True
                self.mousePositions.append(mouse)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.isDragging:
                self.isDragging = False
                self.mousePositions.clear()
        if event.type == pygame.MOUSEWHEEL:
            self.zoom_increment += event.y * 100
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.get_maze()
            if event.key == pygame.K_RETURN:
                if self.isSolving:
                    self.isSolving = False
                    pygame.time.set_timer(pygame.event.Event(DRAW_RECT), 0)
                else:
                    self.isSolving = True
                    pygame.time.set_timer(pygame.event.Event(DRAW_RECT), self.speed)

    def handle_dragging(self):
        if self.isDragging:
            if len(self.mousePositions) > 1:
                change = self.mousePositions[-1] - self.mousePositions[-2]
                self.transform += change
            mouse = pygame.math.Vector2(pygame.mouse.get_pos())
            self.mousePositions.append(mouse)

    def update(self):
        self.handle_dragging()

        if not self.isSolving:
            pygame.time.set_timer(pygame.event.Event(DRAW_RECT), 0)

    def generate_maze(self):
        if self.maze:
            generator_lib.free_maze(self.maze)

        if self.bfs_info:
            solver_lib.free_bfs_info(self.bfs_info)
            self.bfs_info = None

        self.maze = generator_lib.generate_maze(self.cols, self.rows)

    def get_maze(self, **kwargs):
        if kwargs.get("cols"):
            self.cols = kwargs.get("cols")
        if kwargs.get("rows"):
            self.rows = kwargs.get("rows")
        self.generate_maze()
        self.generate_cells()

    def generate_cells(self):
        self.maze_cells = []

        for i in range(self.maze.contents.num_nodes):
            node = self.maze.contents.nodes[i]
            cell_rect = pygame.Rect(
                node.contents.col * self.node_size[0] + 4,
                node.contents.row * self.node_size[1] + 4,
                self.node_size[0],
                self.node_size[1],
            )
            self.maze_cells.append((cell_rect, node))

        self.maze_surf.fill((255, 255, 255))
        self.draw_rects()

    def draw_wall(self, node, rect):
        # draw the walls around the cell
        if node.walls[DIRECTIONS["TOP"]]:
            pygame.draw.line(
                self.maze_surf,
                self.line_color,
                rect.topleft,
                rect.topright,
                self.line_size,
            )
        if node.walls[DIRECTIONS["RIGHT"]]:
            pygame.draw.line(
                self.maze_surf,
                self.line_color,
                rect.topright,
                rect.bottomright,
                self.line_size,
            )
        if node.walls[DIRECTIONS["BOTTOM"]]:
            pygame.draw.line(
                self.maze_surf,
                self.line_color,
                rect.bottomleft,
                rect.bottomright,
                self.line_size,
            )
        if node.walls[DIRECTIONS["LEFT"]]:
            pygame.draw.line(
                self.maze_surf,
                self.line_color,
                rect.topleft,
                rect.bottomleft,
                self.line_size,
            )

    def draw_rect(self, node):
        node = node.contents
        rect = self.maze_cells[node.vertex][0]
        if node.path:
            pygame.draw.rect(self.maze_surf, (0, 255, 255), rect)
        elif node.searched:
            pygame.draw.rect(self.maze_surf, (255, 255, 0), rect)
        else:
            pygame.draw.rect(self.maze_surf, self.bg_color, rect)
        self.draw_wall(node, rect)

    def draw_rects(self):
        for cell in self.maze_cells:
            self.draw_rect(cell[1])

    def draw(self):
        WINDOW.blit(self.image, self.transform)

    def show_solved(self, vertex):
        node = vertex
        while node.contents.parent != -1:
            self.draw_rect(node)
            node = self.maze.contents.nodes[node.contents.parent]

    def bfs_step(self):
        if not self.bfs_info:
            self.bfs_info = solver_lib.create_bfs_info(
                self.maze, 0, (self.cols * self.rows) - 1
            )

        step = solver_lib.bfs_step(self.maze, self.bfs_info)
        if self.bfs_info.contents.solved:
            solver_lib.shortest_path(self.maze)

        maze = self.maze.contents

        if step != -1:
            self.draw_rect(maze.nodes[step])
        else:
            self.show_solved(maze.nodes[self.rows * self.cols - 1])
            self.isSolving = False


def draw(grid, sidebar):
    WINDOW.fill((255, 255, 255))
    grid.draw()
    sidebar.draw(WINDOW)
    pygame.display.update()


def update(grid, sidebar):
    grid.update()
    sidebar.update()
    check_hover(grid, sidebar)


def check_hover(grid, sidebar):
    temp_cursor = False
    if sidebar.check_hover():
        temp_cursor = True
    cursor = temp_cursor

    if not cursor:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)


def main():
    global cursor
    pygame.init()
    pygame.font.init()

    run = True
    cursor = False

    grid = Grid(50, 50, (60, 60), 10)
    sidebar = ui.Sidebar((1200, 0), (200, 800))

    bg = ui.Element((0, 0), (300, 800))
    bg.active = False
    bg.surf.fill((255, 253, 208))

    font = pygame.font.SysFont("calibri", 24)
    test = ui.Text((0, 0), "Hey", font)
    test.active = False
    test.layer = 2

    button = ui.Button((40, 40), (100, 40), "BUTTON", font)
    button.change_layer(3)
    sidebar.add_element(bg, test, button)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            grid.event_handler(event)
            sidebar.event_handler(event)

        draw(grid, sidebar)
        update(grid, sidebar)

    if grid.maze:
        generator_lib.free_maze(grid.maze)
        grid.maze = None

    pygame.quit()
    sys.exit()


main()
