#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>

#include "../include/maze.h"

int **create_grid(int height, int width) {
    int **grid;
    grid = (int **)malloc(height * sizeof(int *));

    if (grid == NULL) {
        fprintf(stderr, "Memory allocation failed for the grid\n");
        return NULL;
    }

    for (int i = 0; i < height; i++) {
        grid[i] = (int *)malloc(width * sizeof(int));

        if (grid[i] == NULL) {
            fprintf(stderr, "Memory allocation failed for row %d\n", i);

            for (int j = 0; j < i; j++) {
                free(grid[j]);
            }
            free(grid);
            return NULL;
        }
        for (int j = 0; j < width; j++) {
            grid[i][j] = 1;
        }
    }
    return grid;
}

node_t *create_node(int vertex, int data, int row, int column) {
    node_t *new_node = (node_t *)malloc(sizeof(node_t));

    if (new_node == NULL) {
        fprintf(stderr, "Memory allocation failed for node vertex %d\n",
                vertex);
        return NULL;
    }

    new_node->vertex = vertex;
    new_node->data = data;
    new_node->row = row;
    new_node->column = column;
    new_node->parent = -1;
    new_node->next = NULL;

    return new_node;
}

maze_t *create_maze(int width, int height, int **grid) {
    maze_t *maze = (maze_t *)malloc(sizeof(maze_t));

    if (maze == NULL) {
        fprintf(stderr, "Memory allocation failed for maze\n");
    }
    // assign the properties
    maze->width = width;
    maze->height = height;
    maze->num_nodes = count_num_nodes(width, height, grid);

    // allocate the entrance and exit
    maze->start = 0;
    maze->end = 0;

    // allocate the adjacency lists
    maze->nodes = (node_t **)malloc(sizeof(node_t *) * maze->num_nodes);
    if (maze->nodes == NULL) {
        fprintf(stderr, "Memory allocation failed for adjacency lists\n");
        free(maze);
        return NULL;
    }

    for (int i = 0; i < maze->num_nodes; i++) {
        maze->nodes[i] = NULL;
    }

    maze->grid = grid;

    // assign the total size
    maze->size = sizeof(*maze);

    return maze;
}

void free_maze(maze_t *maze) {
    for (int i = 0; i < maze->num_nodes; i++) {
        node_t *curr = maze->nodes[i];
        while (curr != NULL) {
            node_t *tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(maze->nodes);

    for (int i = 0; i < maze->height; i++) {
        free(maze->grid[i]);
    }
    free(maze->grid);
    free(maze);
}

void add_edge(maze_t *maze, node_t *src, node_t *dest) {
    node_t *curr = maze->nodes[src->vertex];
    node_t *prev = curr;
    while (true) {
        if (curr == NULL) {
            break;
        }

        if (curr->vertex == dest->vertex) {
            return;
        }
        prev = curr;
        curr = curr->next;
    }
    curr = prev;

    // src edge connects to destination edge
    node_t *new_node =
        create_node(dest->vertex, dest->data, dest->row, dest->column);
    curr->next = new_node;
   }

void print_graph(maze_t *maze) {
    for (int i = 0; i < maze->num_nodes; i++) {
        node_t *curr = maze->nodes[i];
        if (curr == NULL)
            continue;
        printf("\nAdjacency list of vertex %d (r %d, c %d, d %d): ",
               curr->vertex, curr->row, curr->column, curr->data);
        while (curr != NULL) {
            printf("(Vertex %d (%d, %d, %d)) -> ", curr->vertex, curr->row,
                   curr->column, curr->data);
            curr = curr->next;
        }
        printf("NULL");
    }
}

int count_num_nodes(int width, int height, int **grid) {
    int num_nodes = 0;
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            if (grid[i][j] != 1) {
                num_nodes++;
            }
        }
    }
    return num_nodes;
}

node_t *search_for_node(maze_t *maze, int row, int column) {
    for (int i = 0; i < maze->num_nodes; i++) {
        node_t *src = maze->nodes[i];
        if (src != NULL && row == src->row && column == src->column) {
            return src;
        }
    }
    return NULL;
}

void link_neighbours(maze_t *maze, node_t *src) {
    Directions directions[] = {LEFT, RIGHT, UP, DOWN};

    // look in each direction
    for (int i = 0; i < 4; i++) {
        int new_row = src->row;
        int new_column = src->column;

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

        // check if new row or new column is out of bounds
        if (new_column >= maze->width || new_column < 0 ||
            new_row >= maze->height || new_row < 0) {
            continue;
        }

        // searches for node that has the same row and column
        node_t *dest = search_for_node(maze, new_row, new_column);
        if (dest == NULL) {
            continue;
        }

        add_edge(maze, src, dest);
    }
}

void generate_nodes(maze_t *maze, int positions[4]) {
    // create the nodes for every empty space in grid
    int count = 0;
    for (int i = 0; i < maze->height; i++) {
        for (int j = 0; j < maze->width; j++) {
            if (maze->grid[i][j] != 1) {
                node_t *curr = create_node(count, maze->grid[i][j], i, j);
                if (i == positions[0] && j == positions[1]) {
                    curr->data = 2;
                    maze->start = curr->vertex;
                }
                if (i == positions[2] && j == positions[3]) {
                    curr->data = 3;
                    maze->end = curr->vertex;
                }
                maze->nodes[count] = curr;
                count++;
            }
        }
    }

    // create edges based on neighbours for each node
    node_t *curr;
    for (int i = 0; i < maze->num_nodes; i++) {
        curr = maze->nodes[i];
        link_neighbours(maze, curr);
    }
}

// populates the 2d array with 1 (walls)
void populate_grid(int width, int height, int **grid, int number) {
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            grid[i][j] = number;
        }
    }
}

// prints out the maze in a correct format
void print_grid(maze_t *maze) {
    for (int i = 0; i < maze->height; i++) {
        for (int j = 0; j < maze->width; j++) {
            printf("%d ", maze->grid[i][j]);
        }
        printf("\n");
    }
}
