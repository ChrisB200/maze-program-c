import pygame
from pygame.locals import *
import subprocess
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


class Node(ctypes.Structure):
    pass


Node._fields_ = [
    ("vertex", ctypes.c_int),
    ("data", ctypes.c_int),
    ("row", ctypes.c_int),
    ("column", ctypes.c_int),
    ("next", ctypes.POINTER(Node)),
    ("parent", ctypes.c_int),
]


class Maze(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
        ("size", ctypes.c_int),
        ("num_nodes", ctypes.c_int),
        ("nodes", ctypes.POINTER(ctypes.POINTER(Node))),
        ("start", ctypes.c_int),
        ("end", ctypes.c_int),
        ("grid", ctypes.POINTER(ctypes.POINTER(ctypes.c_int))),
    ]


# function prototypes
generator_lib.generate_maze.argtypes = [ctypes.c_int, ctypes.c_int]
generator_lib.generate_maze.restype = ctypes.POINTER(Maze)

generator_lib.free_maze.argtypes = [ctypes.POINTER(Maze)]

generator_lib.print_graph.argtypes = [ctypes.POINTER(Maze)]

generator_lib.print_grid.argtypes = [ctypes.POINTER(Maze)]

solver_lib.solve_maze.argtypes = [ctypes.POINTER(Maze)]


class Grid:
    def __init__(self, width, height, cell_size, filename="maze.txt"):
        self.transform = pygame.math.Vector2()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.filename = filename
        self.maze = None
        self.maze_rects = []
        self.isDragging = False
        self.mousePositions = []
        self.zoom = 1
        self.maze_surface = None
        self.get_maze(width, height)

    def cell_width(self):
        return self.cell_size[0] * self.zoom

    def cell_height(self):
        return self.cell_size[1] * self.zoom

    def maze_width(self):
        return self.cell_size[0] * self.width

    def maze_height(self):
        return self.cell_size[1] * self.height

    def rect(self):
        return pygame.Rect(
            self.transform.x,
            self.transform.y,
            self.maze_width() * self.zoom,
            self.maze_height() * self.zoom,
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
                self.get_maze(self.width, self.height)
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

    def get_maze(self, width, height):
        self.width = width
        self.height = height

        if self.maze:
            generator_lib.free_maze(self.maze)

        self.maze = generator_lib.generate_maze(self.width, self.height)
        print("test")
        self.generate_rects()
        print("generated")

    def generate_rects(self):
        self.maze_rects = []

        for i in range(self.maze.contents.height):
            row = self.maze.contents.grid[i]
            for j in range(self.maze.contents.width):
                cell = row[j]
                cell_rect = pygame.Rect(
                    i * self.cell_size[0],
                    j * self.cell_size[1],
                    self.cell_size[0],
                    self.cell_size[1],
                )
                self.maze_rects.append((cell_rect, cell))

        self.maze_surface = pygame.Surface((self.maze_width(), self.maze_height()))
        self.draw_rects(self.maze_surface)

    def draw_rects(self, surface):
        for cell in self.maze_rects:
            match cell[1]:
                case 0:
                    pygame.draw.rect(surface, (200, 200, 200), cell[0])
                case 1:
                    pygame.draw.rect(surface, (0, 0, 0), cell[0])
                case 2:
                    pygame.draw.rect(surface, (0, 255, 0), cell[0])
                case 3:
                    pygame.draw.rect(surface, (255, 0, 0), cell[0])
                case 4:
                    pygame.draw.rect(surface, (255, 255, 0), cell[0])
                case 5:
                    pygame.draw.rect(surface, (0, 255, 255), cell[0])

    def draw(self):
        if self.maze_surface is None:
            self.maze_surface = pygame.Surface((self.maze_width(), self.maze_height()))
            self.draw_rects(self.maze_surface)

        WINDOW.blit(
            pygame.transform.scale_by(self.maze_surface, (self.zoom, self.zoom)),
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

    grid = Grid(21, 21, (20, 20))

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
