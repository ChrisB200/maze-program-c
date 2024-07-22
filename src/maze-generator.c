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

maze_t *generate_maze(int rows, int cols) {
    srand(time(NULL));

    // generate the maze
    maze_t *maze = create_maze(rows, cols);
    
    int count = 0;
    node_t *curr = NULL;
    for (int i = 0; i < maze->rows; i++) {
        for (int j = 0; j < maze->cols; j++) {
            curr = create_node(count, i, j);
            maze->nodes[count] = curr;
            count++;
        }
    }

    return maze;
}
