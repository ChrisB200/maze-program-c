import pygame_gui
import pygame
import sys
import math
import os
import ctypes
import platform
from enum import IntEnum

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

if platform.system() == "Windows":
    lib_ext = "dll"
else:
    lib_ext = "so"


def load_shared_library(filename, ext):
    path = os.path.join(os.path.dirname(__file__), f"{filename}.{ext}")
    return ctypes.CDLL(path)


# Load the libraries
generator_lib = load_shared_library("lib/libmaze-generator", lib_ext)
solver_lib = load_shared_library("lib/libmaze-solver", lib_ext)


WIDTH, HEIGHT = 1500, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

DIRECTIONS = {"TOP": 0, "RIGHT": 1, "BOTTOM": 2, "LEFT": 3}


class Algorithms(IntEnum):
    BFS = 0
    DJIKSTRA = 1
    ASTAR = 2
    BELLMAN = 3


DRAW_RECT = pygame.USEREVENT + 9999

# Preload the necessary fonts
fonts_to_preload = [
    {"name": "noto_sans", "point_size": 12, "style": "regular", "antialiased": True},
    {"name": "noto_sans", "point_size": 18, "style": "regular", "antialiased": True},
    {"name": "noto_sans", "point_size": 24, "style": "regular", "antialiased": True},
    {"name": "noto_sans", "point_size": 36, "style": "regular", "antialiased": True},
    {"name": "noto_sans", "point_size": 48, "style": "regular", "antialiased": True},
    {"name": "noto_sans", "point_size": 64, "style": "regular", "antialiased": True},
]


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


class SearchInfo(ctypes.Structure):
    _fields_ = [
        ("start", ctypes.c_int),
        ("end", ctypes.c_int),
        ("bfs", ctypes.POINTER(BfsInfo)),
    ]


# function prototypes
generator_lib.generate_maze.argtypes = [ctypes.c_int, ctypes.c_int]
generator_lib.generate_maze.restype = ctypes.POINTER(Maze)

generator_lib.free_maze.argtypes = [ctypes.POINTER(Maze)]

generator_lib.print_graph.argtypes = [ctypes.POINTER(Maze)]

generator_lib.reset_node.argtypes = [ctypes.POINTER(Node)]


solver_lib.solve_maze.argtypes = [ctypes.POINTER(Maze)]

solver_lib.create_search_info.argtypes = [
    ctypes.POINTER(Maze),
    ctypes.c_int,
    ctypes.c_int,
]
solver_lib.create_search_info.restype = ctypes.POINTER(SearchInfo)

solver_lib.free_search_info.argtypes = [ctypes.POINTER(SearchInfo)]

solver_lib.create_bfs_info.argtypes = [ctypes.POINTER(Maze), ctypes.c_int, ctypes.c_int]
solver_lib.create_bfs_info.restype = ctypes.POINTER(BfsInfo)

solver_lib.free_bfs_info.argtypes = [ctypes.POINTER(BfsInfo)]

solver_lib.shortest_path.argtypes = [ctypes.POINTER(Maze), ctypes.POINTER(SearchInfo)]

solver_lib.bfs_step.argtypes = [ctypes.POINTER(Maze), ctypes.POINTER(BfsInfo)]
solver_lib.bfs_step.restype = ctypes.c_int


class Cell:
    def __init__(self, rect, vertex, grid, line_size):
        self.rect = rect
        self.vertex = vertex
        self.grid = grid
        self.line_size = line_size
        self.bg_color = (255, 255, 255)
        self.start_color = pygame.Color(122, 77, 159)
        self.end_color = pygame.Color(34, 35, 95)
        self.hover_color = (200, 200, 200)
        self.line_color = (0, 0, 0)
        self.search_color = pygame.Color(168, 218, 205)
        self.path_color = pygame.Color(235, 104, 160)

        self.state = "bg"

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

    def set_state(self, state, surf):
        self.state = state
        self.draw(surf)

    def draw(self, surf, hover=False):
        if hover:
            pygame.draw.rect(surf, self.hover_color, self.rect)
        elif self.state == "start":
            pygame.draw.rect(surf, self.start_color, self.rect)
        elif self.state == "end":
            pygame.draw.rect(surf, self.end_color, self.rect)
        elif self.state == "path":
            pygame.draw.rect(surf, self.path_color, self.rect)
        elif self.state == "search":
            pygame.draw.rect(surf, self.search_color, self.rect)
        elif self.state == "bg":
            pygame.draw.rect(surf, self.bg_color, self.rect)
        self.draw_wall(surf)


class Grid:
    def __init__(self, rows, cols):
        self.transform = pygame.math.Vector2()
        self.rows = rows
        self.cols = cols
        self.node_size = None
        self.calculate_node_size()
        self.line_size = math.floor(self.node_size[0] * 0.1)

        # c maze info
        self.maze = None
        self.search_info = None

        # movement
        self.zoom_increment = 0
        self.mousePositions = []
        self.isDragging = False
        self.isHolding = False
        self.bounding_rect = pygame.Rect(0, 0, 1200, 800)

        # cells
        self.surf = pygame.Surface(self.get_size())
        self.cells = []
        self.isSolving = False
        self.speed = 1
        self.hovered_cells = []
        self.changed_cells = []
        self.bounds = pygame.math.Vector2(1200, 800)

        # searching
        self.start = None
        self.end = None
        self.current_algorithm = Algorithms.BFS

        self.get_maze()
        self.initial_position()

    @property
    def bfs(self):
        if self.search_info:
            return self.search_info.contents.bfs.contents
        return None

    @property
    def image(self):
        return pygame.transform.smoothscale(
            self.surf,
            (
                self.get_width(),
                self.get_height(),
            ),
        )

    def calculate_node_size(self):
        if self.rows // 800 > 20:
            self.node_size = (self.rows // 800, self.rows // 800)
        else:
            self.node_size = (20, 20)

    def cell_width(self):
        return self.node_size[0] + self.zoom_increment

    def cell_height(self):
        return self.node_size[1] + self.zoom_increment

    def get_width(self):
        return (self.cell_width() * self.cols) + self.line_size

    def get_height(self):
        return (self.cell_height() * self.rows) + self.line_size

    def get_size(self):
        return self.get_width() + 10, self.get_height() + 10

    def get_center(self):
        center_x = self.transform.x - (self.get_width() // 2)
        center_y = self.transform.y - (self.get_height() // 2)
        return pygame.math.Vector2(center_x, center_y)

    def initial_position(self):
        # Assuming WIDTH and HEIGHT are the dimensions of the screen
        center_x = (WIDTH - 300) // 2
        center_y = HEIGHT // 2
        self.transform.x = center_x
        self.transform.y = center_y

    def rect(self):
        return pygame.Rect(
            self.get_center().x,
            self.get_center().y,
            self.get_width(),
            self.get_height(),
        )

    def check_places(self):
        if not self.start or not self.end:
            return False
        return True

    def get_cell(self):
        mouse = pygame.mouse.get_pos()

        if self.rect().collidepoint(mouse):
            outer = pygame.math.Vector2(mouse)
            change = outer - self.get_center()
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
                    cell.set_state(cell.state, self.surf)
                    self.hovered_cells.pop(count)
            if index not in self.hovered_cells:
                self.hovered_cells.append(index)
            if len(self.hovered_cells) == 2:
                cell = self.cells[self.hovered_cells[0]]
                cell.set_state(cell.state, self.surf)
                self.hovered_cells.pop(0)
            self.cells[index].draw(self.surf, hover=True)
        else:
            for count, cell in enumerate(self.hovered_cells):
                cell = self.cells[cell]
                cell.set_state(cell.state, self.surf)
                self.hovered_cells.pop(count)

    def start_solving(self):
        if self.isSolving:
            self.isSolving = False
            pygame.time.set_timer(pygame.event.Event(DRAW_RECT), 0)
        else:
            if self.check_places():
                self.isSolving = True
                pygame.time.set_timer(pygame.event.Event(DRAW_RECT), self.speed)

    def check_sidebar(self, mouse):
        if mouse.x >= 1200:
            return False
        return True

    def create_search_info(self):
        if not self.search_info:
            if self.check_places():
                self.search_info = solver_lib.create_search_info(
                    self.maze, self.start, self.end
                )

    def handle_searching(self):
        self.create_search_info()
        if self.current_algorithm == Algorithms.BFS:
            self.bfs_step()

    def drag_down(self, event):
        mouse = pygame.math.Vector2(pygame.mouse.get_pos())
        if not self.check_sidebar(mouse):
            return
        if not event.button == 1:
            return
        if not self.isHolding:
            return
        if not self.rect().collidepoint(mouse):
            return

        self.isDragging = True
        self.mousePositions.append(mouse)

    def drag_up(self, event):
        if len(self.hovered_cells) == 0:
            return
        mouse = pygame.math.Vector2(pygame.mouse.get_pos())
        if not self.check_sidebar(mouse):
            return

        if event.button == 1 and self.isDragging:
            self.isDragging = False
            self.mousePositions.clear()

        if self.isDragging:
            return
        if self.isHolding:
            return

        # place start color
        if event.button == 1 and self.rect().collidepoint(mouse):
            if self.start:
                self.reset_cells()
                self.cells[self.start].set_state("bg", self.surf)
            self.start = self.hovered_cells[-1]
            self.cells[self.start].set_state("start", self.surf)

        # place end color
        if event.button == 3 and self.rect().collidepoint(mouse):
            if self.end:
                self.cells[self.end].set_state("bg", self.surf)

            self.end = self.hovered_cells[-1]
            self.cells[self.end].set_state("end", self.surf)

    def event_handler(self, event):
        if event.type == DRAW_RECT:
            self.handle_searching()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                self.isHolding = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                self.isHolding = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.drag_down(event)
        if event.type == pygame.MOUSEBUTTONUP:
            self.drag_up(event)
        if event.type == pygame.MOUSEWHEEL:
            self.zoom_increment += event.y
            if self.get_width() <= 20 or self.get_height() <= 20:
                self.zoom_increment -= event.y

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
            self.maze = None

        if self.search_info:
            solver_lib.free_search_info(self.search_info)
            self.search_info = None

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
                node.contents.col * self.node_size[0] + self.line_size,
                node.contents.row * self.node_size[1] + self.line_size,
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
        WINDOW.blit(self.clipped_img, (0, 0))

    def show_solved(self, cell):
        cell = cell
        while cell.node.parent != -1:
            if cell.state != "start" or cell.state != "end":
                cell.set_state("path", self.surf)
            cell = self.cells[cell.node.parent]
        self.cells[self.start].set_state("start", self.surf)
        self.cells[self.end].set_state("end", self.surf)

    def bfs_step(self):
        self.create_search_info()

        if not self.check_places():
            return

        step = solver_lib.bfs_step(self.maze, self.search_info.contents.bfs)
        if self.bfs.solved:
            solver_lib.shortest_path(self.maze, self.search_info)

        if step != -1:
            cell = self.cells[step]
            self.changed_cells.append(cell)
            if cell.state != "start" or cell.state != "end":
                self.cells[step].set_state("search", self.surf)
        else:
            cell = self.cells[self.bfs.end]
            self.show_solved(cell)
            self.isSolving = False

    def reset_cells(self):
        while len(self.changed_cells) > 0:
            for count, cell in enumerate(self.changed_cells):
                generator_lib.reset_node(cell.node_pointer)
                cell.set_state("bg", self.surf)
                self.changed_cells.pop(count)
        if self.search_info:
            solver_lib.free_search_info(self.search_info)
        self.search_info = None


def draw(grid):
    WINDOW.fill((255, 255, 255))
    grid.draw()
    manager.draw_ui(WINDOW)
    pygame.display.update()


def update(grid):
    grid.update()
    manager.update(dt)
    check_hover(grid)


def check_hover(grid):
    temp_cursor = False
    if grid.rect().collidepoint(pygame.mouse.get_pos()):
        temp_cursor = True
    cursor = temp_cursor

    if not cursor:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)


def main():
    global cursor
    global manager
    global dt
    pygame.init()
    pygame.font.init()

    run = True
    cursor = False

    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    manager.preload_fonts(fonts_to_preload)

    grid = Grid(50, 50)

    sidebar = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(1200, 0, 300, 800),
        manager=manager,
        anchors={"centery": "centery"},
    )

    controls_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(-1, 40, 200, 50),
        text="Show Controls",
        manager=manager,
        container=sidebar,
        anchors={"centerx": "centerx"},
    )

    row_lbl = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(-1, 80, -1, -1),
        text="Rows & Columns: 50",
        manager=manager,
        container=sidebar,
        anchors={"centerx": "centerx", "top_target": controls_btn},
    )

    row_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect(0, 20, 250, 30),
        start_value=50,
        value_range=(5, 150),
        manager=manager,
        container=sidebar,
        anchors={"centerx": "centerx", "top_target": row_lbl},
    )

    generate_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(-1, 40, 200, 50),
        text="Generate Maze",
        manager=manager,
        container=sidebar,
        anchors={"centerx": "centerx", "top_target": row_slider},
    )

    algorithm_dropdown = pygame_gui.elements.UIDropDownMenu(
        relative_rect=pygame.Rect(-1, 80, 200, 40),
        options_list=["Breadth-First"],
        starting_option="Breadth-First",
        manager=manager,
        container=sidebar,
        anchors={"centerx": "centerx", "top_target": generate_btn},
    )

    algorithm_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(-1, 40, 200, 50),
        text="Start Search",
        manager=manager,
        container=sidebar,
        anchors={"centerx": "centerx", "top_target": algorithm_dropdown},
    )

    reset_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(-1, 40, 200, 50),
        text="Reset Colours",
        manager=manager,
        container=sidebar,
        anchors={"centerx": "centerx", "top_target": algorithm_btn},
    )

    exit_btn = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(-1, 40, 200, 50),
        text="Exit",
        manager=manager,
        container=sidebar,
        anchors={"centerx": "centerx", "top_target": reset_btn},
    )

    clock = pygame.time.Clock()

    while run:
        dt = clock.tick() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == row_slider:
                    slider_value = row_slider.get_current_value()
                    row_lbl.set_text(f"Rows & Columns: {slider_value}")
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == algorithm_dropdown:
                    selected_option = algorithm_dropdown.selected_option[0]
                    print(selected_option)
                    match selected_option.lower():
                        case "breadth-first":
                            grid.current_algorithm = Algorithms.BFS
                        case "djikstras":
                            grid.current_algorithm = Algorithms.DJIKSTRA
                        case "a*":
                            grid.current_algorithm = Algorithms.ASTAR
                        case "bellman-ford":
                            grid.current_algorithm = Algorithms.BELLMAN

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == generate_btn:
                    row_slider_value = row_slider.get_current_value()
                    grid = Grid(row_slider_value, row_slider_value)
                if event.ui_element == algorithm_btn:
                    grid.start_solving()
                if event.ui_element == reset_btn:
                    grid.reset_cells()
                if event.ui_element == controls_btn:
                    controls_msg = pygame_gui.windows.UIMessageWindow(
                        rect=pygame.Rect(-1, -1, 400, 300),
                        html_message=(
                            "<font size='+6'><p><u>Controls</u></p></font>"
                            "<font size='+4'><p>Drag - Left Mouse Button + Left Shift</p></font>"
                            "<font size='+4'><p>Place Starting Cell - Left Mouse Button</p></font>"
                            "<font size='+4'><p>Place Ending Cell - Right Mouse Button</p></font>"
                            "<font size='+4'><p>Scroll - Scroll Wheel</p></font>"
                        ),
                        manager=manager,
                        window_title="Message",
                    )
                if event.ui_element == exit_btn:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            manager.process_events(event)
            grid.event_handler(event)

        draw(grid)
        update(grid)

    if grid.maze:
        generator_lib.free_maze(grid.maze)
        grid.maze = None
    if grid.search_info:
        generator_lib.free(grid.search_info)
        grid.search_info = None

    pygame.quit()
    sys.exit()


main()
