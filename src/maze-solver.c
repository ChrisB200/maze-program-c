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

bool carve_passage(int row, int column, maze_t *maze) {
    if (row < 0 || row >= maze->height || column < 0 || column >= maze->width) {
        return false;
    }

    if (maze->grid[row][column] == 3) {
        return true;
    }

    if (maze->grid[row][column] == 1) {
        return false;
    }

    Directions directions[] = {LEFT, RIGHT, UP, DOWN};
    int new_row;
    int new_column;
    bool is_solved;

    maze->grid[row][column] = 4;
    randomise_directions(directions);

    for (int i = 0; i < 4; i++) {
        new_row = row;
        new_column = column;
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
        is_solved = carve_passage(new_row, new_column, maze);

        if (is_solved == true) {
            break;
        }
    }

    return is_solved;
}

void recursive_backtracking(maze_t *maze) {
    int entrance_row;
    int entrance_height;
    srand(time(NULL));

    for (int i = 0; i < maze->height; i++) {
        for (int j = 0; j < maze->width; j++) {
            if (maze->grid[i][j] == 2) {
                entrance_row = i;
                entrance_height = j;
            }
        }
    }

    bool is_passage = carve_passage(entrance_row, entrance_height, maze);
    maze->grid[entrance_row][entrance_height] = 2;
}


void shortest_path(maze_t *maze) {
    node_t *entrance = maze->nodes[maze->start];
    node_t *exit = maze->nodes[maze->end];
    node_t *curr = exit;

    while (true) {
        if (curr->parent == -1) {
            continue;
        }

        if (curr->vertex == entrance->vertex) {
            break;
        }

        if (curr == NULL) {
            break;
        }

        curr->data = 5;
        maze->grid[curr->row][curr->column] = 5;
        curr = maze->nodes[curr->parent];
    }
}

void redraw_entrances(maze_t *maze) {
    node_t *entrance = maze->nodes[maze->start];
    node_t *exit = maze->nodes[maze->end];

    maze->grid[entrance->row][entrance->column] = 2;
    maze->grid[exit->row][exit->column] = 3;
}

void bfs(maze_t *maze, int entrance, int exit) {
    int max_size = maze->num_nodes;
    bool visited[max_size];

    // intialise queue
    int queue[max_size];
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

    while (front <= rear) {
        // get vertex from queue
        int vertex = queue[front];
        node_t *curr = maze->nodes[vertex];
        front++;

        // check if the vertex is the exit
        if (vertex == exit)
            break;

        maze->grid[curr->row][curr->column] = 4;

        // add all adjacent vertices to queue
        curr = maze->nodes[vertex];
        while (curr != NULL) {
            if (visited[curr->vertex] == false) {
                // add adjacent vertex to queue
                rear++;
                queue[rear] = curr->vertex;
                visited[curr->vertex] = true;
                maze->nodes[curr->vertex]->parent = vertex;
            }
            curr = curr->next;
        }
    }
    shortest_path(maze);
}

void solve_maze(maze_t *maze) {
    bfs(maze, 0, maze->num_nodes-1);
    redraw_entrances(maze);
}
