#include <stdlib.h>
#include <stdbool.h>
#ifndef MAZE_H
#define MAZE_H

typedef enum { TOP, RIGHT, BOTTOM, LEFT } Directions;

typedef struct node_t {
    int vertex;
    int row;
    int col;
    bool *walls;
    bool visited;
    bool searched;
    bool path;
    int parent;
    struct node_t *next;
} node_t;

typedef struct maze_t {
    int rows;
    int cols;
    int num_nodes;
    node_t **nodes;
    size_t size;
} maze_t;

node_t *create_node(int vertex, int row, int col);
maze_t *create_maze(int rows, int cols);
void free_node(node_t *node);
void free_maze(maze_t *maze);
void add_edge(maze_t *maze, node_t *src, node_t *dest);
void print_graph(maze_t *maze);
node_t *check_cell(maze_t *maze, int row, int col);

#endif
