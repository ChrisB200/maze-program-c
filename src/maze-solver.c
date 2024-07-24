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

bfs_info *create_bfs_info(maze_t *maze, int start, int end) {
    bfs_info *info = (bfs_info *)malloc(sizeof(bfs_info));

    info->max_size = maze->num_nodes;
    info->start = start;
    info->end = end;
    info->rear = -1;
    info->front = 0;
    info->solved = false;

    info->visited = (bool *)malloc(sizeof(bool) * info->max_size);
    for (int i = 0; i < info->max_size; i++) {
        info->visited[i] = false;
    }

    info->queue = (int *)malloc(sizeof(int) * info->max_size);
    for (int i = 0; i < info->max_size; i++) {
        info->queue[i] = 0;
    }

    // add entrance vertex into queue
    info->rear++;
    info->queue[info->rear] = start;
    info->visited[start] = true;
    maze->nodes[start]->path = true;

    return info;
}

void free_bfs_info(bfs_info *info) {
    free(info->visited);
    free(info->queue);
    free(info);
}

void randomise_directions(Directions directions[]) {
    for (int i = 0; i < 4; i++) {
        int j = rand() % 4;
        Directions temp = directions[i];
        directions[i] = directions[j];
        directions[j] = temp;
    }
}

void shortest_path(maze_t *maze) {
    node_t *entrance = maze->nodes[0];
    node_t *exit = maze->nodes[maze->num_nodes-1];
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

int bfs_step(maze_t *maze, bfs_info *info) {
    if (info->solved) {
        return -1;
    }
    // get vertex from queue
    int vertex = info->queue[info->front];
    node_t *curr = maze->nodes[vertex];
    info->front++;

    // check if the vertex is the exit
    if (vertex == info->end) {
        info->solved = true;
        return vertex;
    }

    // add all adjacent vertices to queue
    curr = maze->nodes[vertex];
    while (curr != NULL) {
        if (info->visited[curr->vertex] == false) {
            // add adjacent vertex to queue
            info->rear++;
            info->queue[info->rear] = curr->vertex;
            info->visited[curr->vertex] = true;
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
    int queue[max_size*2];
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
    shortest_path(maze);
}

void solve_maze(maze_t *maze) {
    instant_bfs(maze, 0, maze->num_nodes-1);
}
