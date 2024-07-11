#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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
        //printf("\n%c", cell);

        if (cell == 'S') {
            row++;
            column = 0;
        } else {
            if (i == max_length -1) {
                maze[row][column] = 1;
                continue;
            }
            maze[row][column] = cell - '0';
            column++;
        }
    }

    fclose(maze_data);
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
    FILE *maze_data;

    maze_data = fopen(filename, "r");
    populate_maze(maze_data, maze_width, maze_height, maze);
    show_maze(maze_width, maze_height, maze);
}
