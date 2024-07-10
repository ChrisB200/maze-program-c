import pygame
from pygame.locals import *
import subprocess
import sys


WIDTH, HEIGHT = 1500, 800
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))


class Grid:
    def __init__(self, width, height, cell_size):
        self.transform = pygame.math.Vector2()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.maze = []
        self.maze_rects = []
        self.isDragging = False
        self.mousePositions = []
        self.zoom = 1
        self.maze_image = None

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
            self.transform.x, self.transform.y, self.maze_width() * self.zoom, self.maze_height() * self.zoom
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
        result = subprocess.run("./main", capture_output=True, text=True).stdout

        rows = result.split("\n")

        for row in rows:
            formatted_row = []

            for cell in row:
                if cell == "1" or cell == "0" or cell == "2" or cell == "3":
                    formatted_row.append(int(cell))

            self.maze.append(formatted_row)

        for row in self.maze:
            if row == []:
                self.maze.remove(row)

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

    def draw(self):
        if self.maze_surface is None:
            self.maze_surface = pygame.Surface((self.maze_width(), self.maze_height()))
            self.draw_rects(self.maze_surface)

        WINDOW.blit(
            pygame.transform.scale_by(self.maze_surface, (self.zoom, self.zoom)),
            self.transform,
        )


def draw(grid):
    WINDOW.fill((255, 255, 255))
    grid.draw()
    pygame.display.update()


def update(grid):
    grid.update()


def main():
    run = True
    clock = pygame.time.Clock()

    grid = Grid(21, 21, (20, 20))
    grid.get_maze()

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    grid.get_maze()
            grid.event_handler(event)

        draw(grid)
        update(grid)

    pygame.quit()
    sys.exit()


main()
