#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// 0 is empty
// 1 is wall

enum Directions { LEFT, RIGHT, UP, DOWN };

void populate_maze(int width, int height, int maze[height][width], int number) {
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            // if (i == 0 || i == height - 1 || j == 0 || j == width - 1) {
            //     maze[i][j] = 1;
            // }
            maze[i][j] = number;
        }
    }
}

void show_maze(int width, int height, int maze[height][width]) {
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            printf("%d ", maze[i][j]);
        }
        printf("\n");
    }
}

void randomise_directions(enum Directions directions[]) {
    for (int i = 0; i < 4; i++) {
        int j = rand() % 4;
        enum Directions temp = directions[i];
        directions[i] = directions[j];
        directions[j] = temp;
    }
}

void carve_passage(int row, int column, int width, int height,
                   int maze[height][width], bool visited_cells[height][width]) {
    if (row < 0 || row >= height || column < 0 || column >= width) {
        return;
    }
    visited_cells[row][column] = true;
    maze[row][column] = 0;

    enum Directions directions[] = {LEFT, RIGHT, UP, DOWN};

    randomise_directions(directions);

    for (int i = 0; i < 4; i++) {
        int new_row = row;
        int new_column = column;
        switch (directions[i]) {
        case LEFT:
            new_column -= 2;
            break;
        case RIGHT:
            new_column += 2;
            break;
        case UP:
            new_row -= 2;
            break;
        case DOWN:
            new_row += 2;
            break;
        }

        if (new_row >= 0 && new_row < height && new_column >= 0 &&
            new_column < width && !visited_cells[new_row][new_column]) {
            maze[(row + new_row) / 2][(column + new_column) / 2] =
                0; // Remove the wall between cells
            carve_passage(new_row, new_column, width, height, maze,
                          visited_cells);
        }
    }
}

void create_entrances_new(int width, int height, int maze[height][width]) {
    enum Directions directions[] = {LEFT, RIGHT, UP, DOWN};
    int random_coordinate;

    randomise_directions(directions);

    for (int i = 0; i < 2; i++) {
        switch (directions[i]) {
        case LEFT:
            random_coordinate = rand() % height;
            if (maze[random_coordinate][1] == 0) {
                maze[random_coordinate][0] = 0;
            } else {
                i--;
            }
            break;
        case RIGHT:
            random_coordinate = rand() % height;
            if (maze[random_coordinate][width - 2] == 0) {
                maze[random_coordinate][width - 1] = 0;
            } else {
                i--;
            }
            break;
        case UP:
            random_coordinate = rand() % width;
            if (maze[1][random_coordinate] == 0) {
                maze[0][random_coordinate] = 0;
            } else {
                i--;
            }
            break;
        case DOWN:
            random_coordinate = rand() % width;
            if (maze[height - 2][random_coordinate] == 0) {
                maze[height - 1][random_coordinate] = 0;
            } else {
                i--;
            }
            break;
        }
    }
}

void recursive_backtracking(int width, int height, int maze[height][width]) {
    /* random int between 0 and width */
    int rand_column = (rand() % (width / 2)) * 2 + 1;
    int rand_row = (rand() % (height / 2)) * 2 + 1;

    maze[rand_row][rand_column] = 0;

    bool visited_cells[height][width];
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            visited_cells[i][j] = false;
        }
    }

    carve_passage(rand_row, rand_column, width, height, maze, visited_cells);
    create_entrances_new(width, height, maze);
}

int main(int argc, char *argv[]) {
    int maze_width = 21;
    int maze_height = 21;

    int maze[maze_height][maze_width];

    srand(time(NULL));

    populate_maze(maze_width, maze_height, maze, 1);
    recursive_backtracking(maze_width, maze_height, maze);
    show_maze(maze_width, maze_height, maze);
    return 0;
}
