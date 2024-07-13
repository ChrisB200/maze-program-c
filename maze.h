#ifndef MAZE_H
#define MAZE_H

// 0 is empty
// 1 is wall
// 2 is an entrance
// 3 is an exit
// 4 is a visited cell

typedef struct Node {
    int data;
    int row;
    int column;
    struct Node *next;
} Node;

typedef struct Maze {
    int width;
    int height;
    int num_of_nodes;
    Node *nodes[];
} Maze;

typedef enum { LEFT, RIGHT, UP, DOWN } Directions;

Node *create_node(int data, int row, int column);
Maze *create_maze(int width, int height, int num_of_nodes);
void add_node(Maze *maze, Node *node, int index);
void add_edge(Node *src, Node *dest);
void link_maze_edges(Maze *mazeGraph, int width, int height,
                     int maze[height][width]);
Maze *convert_to_graph(int width, int height, int maze[height][width]);
void show_graph(Maze *maze);

#endif // !DEBUG
