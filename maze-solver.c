#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// 0 is empty
// 1 is wall
// 2 is entrance
// 3 is exit
// 4 is visited

enum Directions { LEFT, RIGHT, DOWN, UP };

void show_maze(int width, int height, int maze[height][width]) {
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            printf("%d ", maze[i][j]);
        }
        printf("\n");
    }
}

void populate_maze(FILE *maze_data, int width, int height,
                   int maze[height][width]) {
    int max_length = (width * height) + height;
    char contents[max_length];
    fgets(contents, max_length, maze_data);

    char cell;
    int row = -1;
    int column;

    for (int i = 0; i < max_length; i++) {
        cell = contents[i];
        // printf("\n%c", cell);

        if (cell == 'S') {
            row++;
            column = 0;
        } else {
            if (i == max_length - 1) {
                maze[row][column] = 1;
                continue;
            }
            maze[row][column] = cell - '0';
            column++;
        }
    }

    fclose(maze_data);
}

void randomise_directions(enum Directions directions[]) {
    for (int i = 0; i < 4; i++) {
        int j = rand() % 4;
        enum Directions temp = directions[i];
        directions[i] = directions[j];
        directions[j] = temp;
    }
}

bool carve_passage(int row, int column, int width, int height,
                   int maze[height][width]) {
    if (row < 0 || row >= height || column < 0 || column >= width) {
        return false;
    }

    if (maze[row][column] == 3) {
        return true;
    }

    if (maze[row][column] == 1) {
        return false;
    }

    enum Directions directions[] = {LEFT, RIGHT, UP, DOWN};
    int new_row;
    int new_column;
    bool is_solved;

    maze[row][column] = 4;
    randomise_directions(directions);

    for (int i = 0; i < 4; i++) {
        new_row = row;
        new_column = column;
        switch (directions[i]) {
        case LEFT:
            new_column--;
            break;
        case RIGHT:
            new_column++;
            break;
        case UP:
            new_row--;
            break;
        case DOWN:
            new_row++;
            break;
        }
        is_solved = carve_passage(new_row, new_column, width, height, maze);

        if (is_solved == true) {
            break;
        }
    }

    return is_solved;
}

void recursive_backtracking(int width, int height, int maze[height][width]) {
    int entrance_row;
    int entrance_height;
    srand(time(NULL));

    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            if (maze[i][j] == 2) {
                entrance_row = i;
                entrance_height = j;
            }
        }
    }

    bool is_passage = carve_passage(entrance_row, entrance_height, width, height, maze);
    maze[entrance_row][entrance_height] = 2;
}

void solve_from_file(char *filename, int width, int height, int maze[height][width]) {
    FILE *maze_data;

    maze_data = fopen(filename, "r");
    populate_maze(maze_data, width, height, maze);
    recursive_backtracking(width, height, maze);

}

int main(int argc, char *argv[]) {
    int maze_width;
    int maze_height;
    char *filename;

    if (argc == 4) {
        maze_width = atoi(argv[1]);
        maze_height = atoi(argv[2]);
        filename = argv[3];
    } else {
        printf("Pass the height and width and filename as arguments");
        return 1;
    }

    int maze[maze_height][maze_width];

    solve_from_file(filename, maze_width, maze_height, maze);
    show_maze(maze_width, maze_height, maze);
}
