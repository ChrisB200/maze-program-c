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

int random_start(maze_t *maze) {
    int random_index;
    node_t *tmp;
    while (true) {
        random_index = rand() % maze->num_nodes;
        tmp = maze->nodes[random_index];
        if (tmp->row < 1 || tmp->row > maze->rows - 1 || tmp->col < 1 ||
            tmp->col > maze->cols - 1) {
            continue;
        }
        return random_index;
    }
}

void check_neighbours(maze_t *maze, node_t *node, node_t *neighbours[4]) {
    Directions directions[4] = {TOP, RIGHT, BOTTOM, LEFT};
    randomise_directions(directions);

    for (int i = 0; i < 4; i++) {
        int new_row = node->row;
        int new_col = node->col;
        switch (directions[i]) {
        case TOP:
            new_row--;
            break;
        case RIGHT:
            new_col++;
            break;
        case BOTTOM:
            new_row++;
            break;
        case LEFT:
            new_col--;
            break;
        }
        node_t *tmp = check_cell(maze, new_row, new_col);
        if (tmp == NULL) {
            continue;
        }

        if (!tmp->visited && tmp != NULL) {
            neighbours[i] = tmp;
        }
    }
}

void create_entrances(maze_t *maze) {
    node_t *entrance = maze->nodes[0];
    node_t *exit = maze->nodes[maze->num_nodes-1];

    entrance->walls[TOP] = false;
    exit->walls[BOTTOM] = false;
}

// creates the maze via backtracking
void backtracking(maze_t *maze) {
    // initialise stack
    node_t *stack[maze->num_nodes];
    int stack_count = 0;

    // initialise node and add to stack
    node_t *curr = maze->nodes[rand() % maze->num_nodes-1];
    curr->visited = true;
    stack[stack_count++] = curr;

    while (stack_count > 0) {
        // pop a node from the stack
        curr = stack[--stack_count];

        // check the neighbours for the node
        node_t *neighbours[4] = {NULL, NULL, NULL, NULL};
        check_neighbours(maze, curr, neighbours);
        
        bool unvisited_neighbour = false;
        for (int i = 0; i < 4; i++) {
            if (neighbours[i] && !neighbours[i]->visited) {
                unvisited_neighbour = true;
                neighbours[i]->visited = true;
                stack[stack_count++] = curr;
                stack[stack_count++] = neighbours[i];

                // neighbour is below current
                if (neighbours[i]->row > curr->row) {
                    neighbours[i]->walls[TOP] = false;
                    curr->walls[BOTTOM] = false; 
                }

                // neighbour is above current
                if (neighbours[i]->row < curr->row) {
                    neighbours[i]->walls[BOTTOM] = false;
                    curr->walls[TOP] = false;
                }

                // neighbour is on the right of current
                if (neighbours[i]->col > curr->col) {
                    neighbours[i]->walls[LEFT] = false;
                    curr->walls[RIGHT] = false;
                }

                // neighbour is on the left of current
                if (neighbours[i]->col < curr->col) {
                    neighbours[i]->walls[RIGHT] = false;
                    curr->walls[LEFT] = false;
                }
                add_edge(maze, curr, neighbours[i]);
                add_edge(maze, neighbours[i], curr);
                break;
            }
        }
        if (!unvisited_neighbour) {
            stack_count--;
        }

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

    backtracking(maze);
    create_entrances(maze);

    return maze;
}

int main() {
    maze_t *maze = generate_maze(20, 20);
    free_maze(maze);
    return 0;
}
