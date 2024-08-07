#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>

#include "../include/maze.h"

node_t *create_node(int vertex, int row, int col)
{
    node_t *new_node = (node_t *)malloc(sizeof(node_t));

    if (new_node == NULL)
    {
        fprintf(stderr, "Memory allocation failed for node vertex %d\n",
                vertex);
        return NULL;
    }

    // assign values
    new_node->vertex = vertex;
    new_node->row = row;
    new_node->col = col;

    new_node->walls = (bool *)malloc(sizeof(bool *) * 4);

    // set default values for walls
    for (int i = 0; i < 4; i++)
    {
        new_node->walls[i] = true;
    }
    new_node->visited = false;
    new_node->searched = false;
    new_node->path = false;
    new_node->next = NULL;
    new_node->parent = -1;

    return new_node;
}

maze_t *create_maze(int rows, int cols)
{
    maze_t *maze = (maze_t *)malloc(sizeof(maze_t));

    if (maze == NULL)
    {
        fprintf(stderr, "Memory allocation failed for maze\n");
    }

    // assign the properties
    maze->rows = rows;
    maze->cols = cols;
    maze->num_nodes = rows * cols;

    // allocate the adjacency lists (array of linked lists)
    maze->nodes = (node_t **)malloc(sizeof(node_t *) * maze->num_nodes);
    if (maze->nodes == NULL)
    {
        fprintf(stderr, "Memory allocation failed for adjacency lists\n");
        free(maze);
        return NULL;
    }

    for (int i = 0; i < maze->num_nodes; i++)
    {
        maze->nodes[i] = NULL;
    }

    // assign the total size
    maze->size = sizeof(*maze);

    return maze;
}

void free_node(node_t *node)
{
    // free all nodes in linked list
    while (node != NULL)
    {
        node_t *tmp = node;
        node = node->next;
        free(tmp->walls);
        free(tmp);
        tmp = NULL;
    }
}

void free_maze(maze_t *maze)
{
    // free all the nodes
    for (int i = 0; i < maze->num_nodes; i++)
    {
        node_t *curr = maze->nodes[i];
        free_node(curr);
    }
    free(maze->nodes);
    free(maze);
}

node_t *copy_node(node_t *src)
{
    node_t *new_node = create_node(src->vertex, src->row, src->col);
    new_node->visited = src->visited;
    new_node->searched = src->searched;
    // Deep copy the walls array
    memcpy(new_node->walls, src->walls, sizeof(bool) * 4);
    return new_node;
}

void add_edge(maze_t *maze, node_t *src, node_t *dest)
{
    node_t *curr = src;
    node_t *tmp;
    while (true)
    {
        if (curr == NULL)
        {
            break;
        }
        tmp = curr;
        curr = curr->next;
    }

    node_t *dest_copy = copy_node(dest);
    tmp->next = dest_copy;
}

void print_graph(maze_t *maze)
{
    for (int i = 0; i < maze->num_nodes; i++)
    {
        node_t *curr = maze->nodes[i];
        if (curr == NULL)
            continue;
        printf("\nAdjacency list of vertex %d (r %d, c %d): ", curr->vertex,
               curr->row, curr->col);
        while (curr != NULL)
        {
            printf("(Vertex %d (%d, %d)) -> ", curr->vertex, curr->row,
                   curr->col);
            curr = curr->next;
        }
        printf("NULL");
    }
}

node_t *check_cell(maze_t *maze, int row, int col)
{
    if (row < 0 || row >= maze->rows || col < 0 || col >= maze->cols)
    {
        return NULL;
    }
    int index = col + row * maze->cols;
    node_t *tmp = maze->nodes[index];
    return tmp;
}

void reset_node(node_t *node)
{
    node->path = false;
    node->searched = false;
    node->parent = -1;
}
