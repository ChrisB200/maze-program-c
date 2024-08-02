#include "../include/maze.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct {
    int max_size;
    int start;
    int end;
    int rear;
    int front;
    bool solved;
    bool *visited;
    int *queue;
} bfs_info;

typedef struct {
    int max_size;
    int start;
    int end;
    int top;
    bool solved;
    bool *visited;
    int *stack;
} dfs_info;

typedef struct {
    int start;
    int end;
    bfs_info *bfs;
} search_info;

bfs_info *create_bfs_info(maze_t *maze, int start, int end) {
    bfs_info *bfs = (bfs_info *)malloc(sizeof(bfs_info));

    bfs->max_size = maze->num_nodes;
    bfs->start = start;
    bfs->end = end;
    bfs->rear = -1;
    bfs->front = 0;
    bfs->solved = false;

    bfs->visited = (bool *)malloc(sizeof(bool) * bfs->max_size);
    for (int i = 0; i < bfs->max_size; i++) {
        bfs->visited[i] = false;
    }

    bfs->queue = (int *)malloc(sizeof(int) * bfs->max_size);
    for (int i = 0; i < bfs->max_size; i++) {
        bfs->queue[i] = 0;
    }

    // add entrance vertex into queue
    bfs->rear++;
    bfs->queue[bfs->rear] = start;
    bfs->visited[start] = true;
    maze->nodes[start]->path = true;

    return bfs;
}

void free_bfs_info(bfs_info *bfs) {
    free(bfs->visited);
    free(bfs->queue);
    free(bfs);
}

search_info *create_search_info(maze_t *maze, int start, int end) {
    search_info *info = (search_info *)malloc(sizeof(search_info));

    info->start = start;
    info->end = end;
    info->bfs = create_bfs_info(maze, start, end);
    info->dfs = create_dfs_info(maze, start, end);
    return info;
}

void free_search_info(search_info *info) {
    if (info->bfs != NULL) {
        free_bfs_info(info->bfs);
    }
    if (info->dfs != NULL) {
        free_dfs_info(info->dfs);
    }
    free(info);
}

void shortest_path(maze_t *maze, search_info *info) {
    node_t *entrance = maze->nodes[info->start];
    node_t *exit = maze->nodes[info->end];
    node_t *curr = exit;

    while (true) {
        if (curr->parent == -1) {
            break;
        }

        if (curr->vertex == entrance->vertex) {
            break;
        }

        if (curr == NULL) {
            break;
        }

        curr->path = true;
        curr = maze->nodes[curr->parent];
    }
}

int bfs_step(maze_t *maze, bfs_info *bfs) {
    if (bfs->solved) {
        return -1;
    }
    // get vertex from queue
    int vertex = bfs->queue[bfs->front];
    node_t *curr = maze->nodes[vertex];
    bfs->front++;

    // check if the vertex is the exit
    if (vertex == bfs->end) {
        bfs->solved = true;
        return vertex;
    }

    // add all adjacent vertices to queue
    curr = maze->nodes[vertex];
    while (curr != NULL) {
        if (bfs->visited[curr->vertex] == false) {
            // add adjacent vertex to queue
            bfs->rear++;
            bfs->queue[bfs->rear] = curr->vertex;
            bfs->visited[curr->vertex] = true;
            maze->nodes[curr->vertex]->parent = vertex;
            maze->nodes[curr->vertex]->searched = true;
        }
        curr = curr->next;
    }
    return vertex;
}

void instant_bfs(maze_t *maze, int entrance, int exit) {
    int max_size = maze->num_nodes;
    bool visited[max_size];

    // intialise queue
    int queue[max_size * 2];
    int rear = -1;
    int front = 0;

    // initialise boolean array
    for (int i = 0; i < max_size; i++) {
        visited[i] = false;
    }

    // add entrance vertex into queue
    rear++;
    queue[rear] = entrance;
    visited[entrance] = true;
    maze->nodes[entrance]->path = true;

    while (front <= rear) {
        // get vertex from queue
        int vertex = queue[front];
        node_t *curr = maze->nodes[vertex];
        front++;

        // check if the vertex is the exit
        if (vertex == exit)
            break;

        // add all adjacent vertices to queue
        curr = maze->nodes[vertex];
        while (curr != NULL) {
            if (visited[curr->vertex] == false) {
                // add adjacent vertex to queue
                rear++;
                queue[rear] = curr->vertex;
                visited[curr->vertex] = true;
                maze->nodes[curr->vertex]->parent = vertex;
                maze->nodes[curr->vertex]->searched = true;
            }
            curr = curr->next;
        }
    }
}

void solve_maze(maze_t *maze) { instant_bfs(maze, 0, maze->num_nodes - 1); }
