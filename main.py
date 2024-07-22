import pygame
from pygame.locals import *
import sys
import os
import ctypes


def load_shared_library(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    return ctypes.CDLL(path)


WIDTH, HEIGHT = 1500, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

generator_lib = load_shared_library("lib/maze-generator.so")
solver_lib = load_shared_library("lib/maze-solver.so")
DIRECTIONS = {"TOP": 0, "RIGHT": 1, "BOTTOM": 2, "LEFT": 3}


class Node(ctypes.Structure):
    pass


Node._fields_ = [
    ("vertex", ctypes.c_int),
    ("row", ctypes.c_int),
    ("col", ctypes.c_int),
    ("walls", ctypes.POINTER(ctypes.c_bool)),
    ("visited", ctypes.c_bool),
    ("searched", ctypes.c_bool),
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


# function prototypes
generator_lib.generate_maze.argtypes = [ctypes.c_int, ctypes.c_int]
generator_lib.generate_maze.restype = ctypes.POINTER(Maze)

generator_lib.free_maze.argtypes = [ctypes.POINTER(Maze)]

generator_lib.print_graph.argtypes = [ctypes.POINTER(Maze)]

solver_lib.solve_maze.argtypes = [ctypes.POINTER(Maze)]


class Grid:
    def __init__(self, rows, cols, node_size, line_size):
        self.transform = pygame.math.Vector2()
        self.rows = rows
        self.cols = cols
        self.node_size = node_size
        self.line_size = line_size

        self.maze = None
        self.maze_surf = None
        self.maze_rects = []
        self.isDragging = False
        self.mousePositions = []
        self.zoom = 1
        self.get_maze()

    @property
    def image(self):
        if self.maze_surf:
            return self.maze_surf.scale_by(self.maze_surf, (self.zoom, self.zoom))

    def cell_width(self):
        return self.node_size[0] * self.zoom

    def cell_height(self):
        return self.node_size[1] * self.zoom

    def get_width(self):
        return self.node_size[0] * self.cols

    def get_height(self):
        return self.node_size[1] * self.rows

    def rect(self):
        return pygame.Rect(
            self.transform.x,
            self.transform.y,
            self.get_width() * self.zoom,
            self.get_height() * self.zoom,
        )

    def event_handler(self, event):
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
            self.zoom += event.y * 0.1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.get_maze()
            if event.key == pygame.K_RETURN:
                self.solve_maze()

    def handle_dragging(self):
        if self.isDragging:
            if len(self.mousePositions) > 1:
                change = self.mousePositions[-1] - self.mousePositions[-2]
                self.transform += change
            mouse = pygame.math.Vector2(pygame.mouse.get_pos())
            self.mousePositions.append(mouse)

    def update(self):
        self.handle_dragging()

    def get_maze(self, **kwargs):
        if kwargs.get("cols"):
            self.cols = kwargs.get("cols")
        if kwargs.get("rows"):
            self.rows = kwargs.get("rows")

        if self.maze:
            generator_lib.free_maze(self.maze)

        self.maze = generator_lib.generate_maze(self.cols, self.rows)
        self.generate_rects()

    def generate_rects(self):
        self.maze_rects = []

        for i in range(self.maze.contents.num_nodes):
            node = self.maze.contents.nodes[i]
            print(node.contents.vertex)
            cell_rect = pygame.Rect(
                node.contents.col * self.node_size[0] + self.line_size,
                node.contents.row * self.node_size[1] + self.line_size,
                self.node_size[0],
                self.node_size[1],
            )
            self.maze_rects.append((cell_rect, node))

        self.maze_surf = pygame.Surface(
            (self.get_width() + self.line_size * 2, self.get_height() + self.line_size * 2)
        )
        self.draw_rects(self.maze_surf)

    def draw_rects(self, surface):
        for cell in self.maze_rects:
            rect = cell[0]
            node = cell[1].contents
            pygame.draw.rect(surface, (200, 200, 200), rect)

            # draw the walls around the cell
            if node.walls[DIRECTIONS["TOP"]]:
                pygame.draw.line(
                    surface, (0, 0, 0), rect.topleft, rect.topright, self.line_size
                )
            if node.walls[DIRECTIONS["RIGHT"]]:
                pygame.draw.line(
                    surface, (0, 0, 0), rect.topright, rect.bottomright, self.line_size
                )
            if node.walls[DIRECTIONS["BOTTOM"]]:
                pygame.draw.line(
                    surface,
                    (0, 0, 0),
                    rect.bottomleft,
                    rect.bottomright,
                    self.line_size,
                )
            if node.walls[DIRECTIONS["LEFT"]]:
                pygame.draw.line(
                    surface, (0, 0, 0), rect.topleft, rect.bottomleft, self.line_size
                )

    def draw(self):
        if self.maze_surf is None:
            self.maze_surf = pygame.Surface((self.get_width(), self.get_height()))
            self.draw_rects(self.maze_surf)

        WINDOW.blit(
            pygame.transform.scale_by(self.maze_surf, (self.zoom, self.zoom)),
            self.transform,
        )

    def solve_maze(self):
        if self.maze:
            solver_lib.solve_maze(self.maze)
        self.generate_rects()


def draw(grid):
    WINDOW.fill((255, 255, 255))
    grid.draw()
    pygame.display.update()


def update(grid):
    grid.update()


def main():
    pygame.init()
    pygame.font.init()

    run = True

    clock = pygame.time.Clock()

    grid = Grid(21, 21, (20, 20), 3)

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            grid.event_handler(event)

        draw(grid)
        update(grid)

    if grid.maze:
        generator_lib.free_maze(grid.maze)
        grid.maze = None

    pygame.quit()
    sys.exit()


main()
