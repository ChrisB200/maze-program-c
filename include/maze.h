#ifndef MAZE_H
#define MAZE_H

// 0 is empty
// 1 is wall
// 2 is an entrance
// 3 is an exit
// 4 is a visited cell

typedef struct node_t {
    int vertex;
    int data;
    int row;
    int column;
    int parent;
    struct node_t *next;
} node_t;

typedef struct maze_t {
    int width;
    int height;
    int size;
    int num_nodes;
    node_t **nodes;
    int start;
    int end;
    int **grid;
} maze_t;

typedef enum { LEFT, RIGHT, UP, DOWN } Directions;

int **create_grid(int height, int width);
node_t *create_node(int vertex, int data, int row, int column);
maze_t *create_maze(int width, int height, int **grid);
void free_maze(maze_t *maze);
void add_edge(maze_t *maze, node_t *src, node_t *dest);
void print_graph(maze_t *maze);
int count_num_nodes(int width, int height, int **grid);
node_t *search_for_node(maze_t *maze, int row, int column);
void link_neighbours(maze_t *maze, node_t *src);
void generate_nodes(maze_t *maze, int positions[4]);
void populate_grid(int width, int height, int **grid, int number);
void print_grid(maze_t *maze);

#endif
