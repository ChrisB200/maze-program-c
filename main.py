import pygame
from pygame.locals import *
import subprocess
import sys
import os


WIDTH, HEIGHT = 1500, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))


class TextBox:
    def __init__(self, x, y, font, text=""):
        self.transform = pygame.math.Vector2((x, y))
        self.font = font
        self.text = text
        self.isSelected = False
        self.textSurface = pygame.Surface((0, 0))

    def update(self):
        self.textSurface = self.font.render(self.text, True, (0, 0, 0))


    def event_handler(self, event):
        if event.type == pygame.KEYDOWN:
            if self.isSelected:
                self.text += event.unicode

    def draw(self):
        WINDOW.blit(
            self.textSurface,
            (
                self.transform.x - self.textSurface.get_width() // 2,
                self.transform.y - self.textSurface.get_height() // 2,
            ),
        )


class Grid:
    def __init__(self, width, height, cell_size, filename="maze.txt"):
        self.transform = pygame.math.Vector2()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.filename = filename
        self.maze = []
        self.maze_rects = []
        self.isDragging = False
        self.mousePositions = []
        self.zoom = 1
        self.maze_surface = None

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

    def get_maze(self):
        self.maze = []
        cmd = ["./maze-generator", str(self.width), str(self.height)]

        if not os.path.exists("./maze-generator"):
            print("Error: Executable './maze-generator' not found.")
            return

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return

        rows = result.stdout.split("\n")
        for row in rows:
            formatted_row = []

            for cell in row:
                if cell in "01234":
                    formatted_row.append(int(cell))

            self.maze.append(formatted_row)

        for row in self.maze:
            if row == []:
                self.maze.remove(row)

        with open(self.filename, "w") as file:
            for count, row in enumerate(self.maze):
                row_string = "S"
                for cell in row:
                    row_string = row_string + str(cell)

                file.write(row_string)

        self.generate_rects()

    def generate_rects(self):
        self.maze_rects = []
        for county, row in enumerate(self.maze):
            for countx, cell in enumerate(row):
                cell_rect = pygame.Rect(
                    countx * self.cell_size[0],
                    county * self.cell_size[1],
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

    def draw(self):
        if self.maze_surface is None:
            self.maze_surface = pygame.Surface((self.maze_width(), self.maze_height()))
            self.draw_rects(self.maze_surface)

        WINDOW.blit(
            pygame.transform.scale_by(self.maze_surface, (self.zoom, self.zoom)),
            self.transform,
        )

    def solve_maze(self):
        self.maze = []
        cmd = ["./maze-solver", str(self.width), str(self.height), self.filename]

        if not os.path.exists("./maze-solver"):
            print("Error: Executable './maze-solver' not found.")
            return

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return

        rows = result.stdout.split("\n")
        for row in rows:
            formatted_row = []

            for cell in row:
                if cell in "01234":
                    formatted_row.append(int(cell))

            self.maze.append(formatted_row)

        for row in self.maze:
            if row == []:
                self.maze.remove(row)

        self.generate_rects()


def draw(grid, heightTextBox):
    WINDOW.fill((255, 255, 255))
    grid.draw()
    heightTextBox.draw()
    pygame.display.update()


def update(grid, heightTextBox):
    grid.update()
    heightTextBox.update()


def main():
    pygame.init()
    pygame.font.init()

    run = True
    font = pygame.font.SysFont("Arial", 36)

    heightTextBox = TextBox(20, 20, font, "height")
    clock = pygame.time.Clock()

    grid = Grid(31, 31, (20, 20))
    grid.get_maze()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            grid.event_handler(event)
            heightTextBox.event_handler(event)

        draw(grid, heightTextBox)
        update(grid, heightTextBox)

    pygame.quit()
    sys.exit()


main()
