#include "../include/maze.h"
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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

void bfs(maze_t *maze, int entrance, int exit) {
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
    bfs(maze, 0, maze->num_nodes-1);
}
