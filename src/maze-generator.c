#include "../include/maze.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// randomises the 4 directions
void randomise_directions(Directions directions[]) {
    for (int i = 0; i < 4; i++) {
        int j = rand() % 4;
        Directions temp = directions[i];
        directions[i] = directions[j];
        directions[j] = temp;
    }
}

void carve_passage(int row, int column, int width, int height, int **grid,
                   bool visited_cells[height][width]) {
    if (row < 0 || row >= height || column < 0 || column >= width) {
        return;
    }
    visited_cells[row][column] = true;
    grid[row][column] = 0;

    Directions directions[] = {LEFT, RIGHT, UP, DOWN};

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
            grid[(row + new_row) / 2][(column + new_column) / 2] =
                0; // Remove the wall between cells
            carve_passage(new_row, new_column, width, height, grid,
                          visited_cells);
        }
    }
}

// creates both an entrance and exit in the maze
void create_entrances(int width, int height, int **grid, int positions[4]) {
    Directions directions[] = {LEFT, RIGHT, UP, DOWN};
    int random_coordinate;
    int cell_value;

    randomise_directions(directions);

    // creates both entrances and exits randomly
    for (int i = 0; i < 2; i++) {
        // checks whether its an entrance or exit
        if (i == 0) {
            cell_value = 2;
        } else {
            cell_value = 3;
        }

        // randomly go in the direction if it neighbours a passage
        switch (directions[i]) {
        case LEFT:
            random_coordinate = rand() % height;
            if (grid[random_coordinate][1] == 0) {
                grid[random_coordinate][0] = cell_value;
                positions[i + i] = random_coordinate;
                positions[i + i + 1] = 0;
            } else {
                i--;
            }
            break;
        case RIGHT:
            random_coordinate = rand() % height;
            if (grid[random_coordinate][width - 2] == 0) {
                grid[random_coordinate][width - 1] = cell_value;
                positions[i + i] = random_coordinate;
                positions[i + i + 1] = width - 1;
            } else {
                i--;
            }
            break;
        case UP:
            random_coordinate = rand() % width;
            if (grid[1][random_coordinate] == 0) {
                grid[0][random_coordinate] = cell_value;
                positions[i + i] = 0;
                positions[i + i + 1] = random_coordinate;
            } else {
                i--;
            }
            break;
        case DOWN:
            random_coordinate = rand() % width;
            if (grid[height - 2][random_coordinate] == 0) {
                grid[height - 1][random_coordinate] = cell_value;
                positions[i + i] = height - 1;
                positions[i + i + 1] = random_coordinate;
            } else {
                i--;
            }
            break;
        }
    }
}

// recursively generates the maze via backtracking
void recursive_backtracking(int width, int height, int **grid,
                            int positions[4]) {
    // choose a random column and row
    int rand_column = (rand() % (width / 2)) * 2 + 1;
    int rand_row = (rand() % (height / 2)) * 2 + 1;

    grid[rand_row][rand_column] = 0;

    // initialises the visited cells
    bool visited_cells[height][width];
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            visited_cells[i][j] = false;
        }
    }

    carve_passage(rand_row, rand_column, width, height, grid, visited_cells);
    create_entrances(width, height, grid, positions);
    printf("\nEntrance %d %d, EXIT %d %d", positions[0], positions[1],
           positions[2], positions[3]);
    printf("\ntext");
}

maze_t *generate_maze(int width, int height) {
    srand(time(NULL));

    // generate the grid
    int **grid = create_grid(height, width);
    int positions[4];
    populate_grid(width, height, grid, 1);
    recursive_backtracking(width, height, grid, positions);

    // generate the maze
    maze_t *maze = create_maze(width, height, grid);
    generate_nodes(maze, positions);
    node_t *entrance = maze->nodes[maze->start];
    node_t *exit = maze->nodes[maze->end];
    printf("\nentrance vertex %d: r %d c %d d %d", entrance->vertex,
           entrance->row, entrance->column, entrance->data);
    printf("\nexit vertex %d: r %d c %d d %d", exit->vertex,
           exit->row, exit->column, exit->data);

    return maze;
}
