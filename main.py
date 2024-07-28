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

generator_lib.reset_node.argtypes = [ctypes.POINTER(Node)]

solver_lib.solve_maze.argtypes = [ctypes.POINTER(Maze)]

solver_lib.create_bfs_info.argtypes = [ctypes.POINTER(Maze), ctypes.c_int, ctypes.c_int]
solver_lib.create_bfs_info.restype = ctypes.POINTER(BfsInfo)

solver_lib.free_bfs_info.argtypes = [ctypes.POINTER(BfsInfo)]

solver_lib.shortest_path.argtypes = [ctypes.POINTER(Maze)]

solver_lib.bfs_step.argtypes = [ctypes.POINTER(Maze), ctypes.POINTER(BfsInfo)]
solver_lib.bfs_step.restypes = ctypes.c_int


class Cell:
    def __init__(self, rect, vertex, grid, line_size):
        self.rect = rect
        self.vertex = vertex
        self.grid = grid
        self.line_size = line_size
        self.bg_color = (255, 255, 255)
        self.search_color = (255, 255, 0)
        self.path_color = (0, 255, 255)
        self.hover_color = (0, 255, 0)
        self.line_color = (0, 0, 0)

    @property
    def maze(self):
        return self.grid.maze.contents

    @property
    def node(self):
        return self.maze.nodes[self.vertex].contents

    @property
    def node_pointer(self):
        return self.maze.nodes[self.vertex]

    def draw_wall(self, surf):
        # draw the walls around the cell
        if self.node.walls[DIRECTIONS["TOP"]]:
            pygame.draw.line(
                surf,
                self.line_color,
                self.rect.topleft,
                self.rect.topright,
                self.line_size,
            )
        if self.node.walls[DIRECTIONS["RIGHT"]]:
            pygame.draw.line(
                surf,
                self.line_color,
                self.rect.topright,
                self.rect.bottomright,
                self.line_size,
            )
        if self.node.walls[DIRECTIONS["BOTTOM"]]:
            pygame.draw.line(
                surf,
                self.line_color,
                self.rect.bottomleft,
                self.rect.bottomright,
                self.line_size,
            )
        if self.node.walls[DIRECTIONS["LEFT"]]:
            pygame.draw.line(
                surf,
                self.line_color,
                self.rect.topleft,
                self.rect.bottomleft,
                self.line_size,
            )

    def draw(self, surf, hover=False):
        if hover:
            pygame.draw.rect(surf, self.hover_color, self.rect)
        elif self.node.path:
            pygame.draw.rect(surf, self.path_color, self.rect)
        elif self.node.searched:
            pygame.draw.rect(surf, self.search_color, self.rect)
        else:
            pygame.draw.rect(surf, self.bg_color, self.rect)
        self.draw_wall(surf)


class Grid:
    def __init__(
        self,
        rows,
        cols,
        node_size,
        line_size,
    ):
        self.transform = pygame.math.Vector2()
        self.rows = rows
        self.cols = cols
        self.node_size = node_size
        self.line_size = line_size

        # c maze info
        self.maze = None
        self.bfs_info = None

        # movement
        self.zoom = 1
        self.zoom_increment = 0
        self.mousePositions = []
        self.isDragging = False

        # cells
        self.surf = pygame.Surface(self.get_size())
        self.cells = []
        self.isSolving = False
        self.speed = 1
        self.hovered_cells = []
        self.changed_cells = []

        self.get_maze()

    @property
    def image(self):
        return pygame.transform.scale(
            self.surf,
            (
                self.get_width(),
                self.get_height(),
            ),
        )

    def cell_width(self):
        return self.node_size[0] + self.zoom_increment

    def cell_height(self):
        return self.node_size[1] + self.zoom_increment

    def get_width(self):
        return (self.cell_width() * self.cols) + self.line_size

    def get_height(self):
        return (self.cell_height() * self.rows) + self.line_size

    def get_size(self):
        return self.get_width(), self.get_height()

    def rect(self):
        return pygame.Rect(
            self.transform.x,
            self.transform.y,
            self.get_width(),
            self.get_height(),
        )

    def get_cell(self):
        mouse = pygame.mouse.get_pos()

        if self.rect().collidepoint(mouse):
            outer = pygame.math.Vector2(mouse)
            change = outer - self.transform
            col = int(change.x / self.cell_width())
            row = int(change.y / self.cell_height())

            if row >= self.rows:
                return
            if col >= self.rows:
                return
            if col < 0:
                return
            if row < 0:
                return

            index = (row * self.rows) + col
            if index >= self.rows * self.cols or index < 0:
                for count, cell in enumerate(self.hovered_cells):
                    cell = self.cells[cell]
                    cell.draw(self.surf, hover=False)
                    self.hovered_cells.pop(count)
            if index not in self.hovered_cells:
                self.hovered_cells.append(index)
            if len(self.hovered_cells) == 2:
                cell = self.cells[self.hovered_cells[0]]
                cell.draw(self.surf, hover=False)
                self.hovered_cells.pop(0)
            self.cells[index].draw(self.surf, hover=True)
        else:
            for count, cell in enumerate(self.hovered_cells):
                cell = self.cells[cell]
                cell.draw(self.surf, hover=False)
                self.hovered_cells.pop(count)

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
            self.zoom_increment += event.y * 5
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.get_maze()
            if event.key == pygame.K_q:
                self.reset_cells()
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
        self.get_cell()

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
        self.cells.clear()

        for i in range(self.maze.contents.num_nodes):
            node = self.maze.contents.nodes[i]
            cell_rect = pygame.Rect(
                node.contents.col * self.node_size[0] + 4,
                node.contents.row * self.node_size[1] + 4,
                self.node_size[0],
                self.node_size[1],
            )
            cell = Cell(cell_rect, node.contents.vertex, self, self.line_size)
            self.cells.append(cell)

        self.surf.fill((255, 255, 255))
        self.draw_rects()

    def draw_rects(self):
        for cell in self.cells:
            cell.draw(self.surf)

    def draw(self):
        pygame.draw.rect(WINDOW, (255, 0, 0), self.rect())
        WINDOW.blit(self.image, self.transform)

    def show_solved(self, cell):
        cell = cell
        while cell.node.parent != -1:
            cell.draw(self.surf)
            cell = self.cells[cell.node.parent]

    def bfs_step(self):
        if not self.bfs_info:
            self.bfs_info = solver_lib.create_bfs_info(
                self.maze, 0, (self.cols * self.rows) - 1
            )

        step = solver_lib.bfs_step(self.maze, self.bfs_info)
        if self.bfs_info.contents.solved:
            solver_lib.shortest_path(self.maze)

        if step != -1:
            self.changed_cells.append(self.cells[step])
            self.cells[step].draw(self.surf)
        else:
            cell = self.cells[self.bfs_info.contents.end]
            self.show_solved(cell)
            self.isSolving = False

    def reset_cells(self):
        while len(self.changed_cells) > 0:
            for count, cell in enumerate(self.changed_cells):
                generator_lib.reset_node(cell.node_pointer)
                cell.draw(self.surf)
                self.changed_cells.pop(count)
        self.bfs_info = None


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
    if grid.rect().collidepoint(pygame.mouse.get_pos()):
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
