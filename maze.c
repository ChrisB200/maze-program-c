#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <string.h>

#include "maze.h"

Node *create_node(int data, int row, int column) {
    Node *node = (Node *)malloc(sizeof(Node));

    node->data = data;
    node->row = row;
    node->column = column;
    node->next = NULL;

    return node;
}

Maze *create_maze(int width, int height, int num_of_nodes) {
    Maze *maze = (Maze *)malloc(sizeof(Maze) + sizeof(Node) * num_of_nodes);

    maze->width = width;
    maze->height = height;

    for (int i = 0; i < num_of_nodes; i++) {
        maze->nodes[i] = NULL;
    }

    return maze;
}

void add_node(Maze *maze, Node *node, int index) {
    if (maze == NULL || node == NULL)
        printf("\nError adding node to maze");

    maze->nodes[index] = node;
}

void add_edge(Node *src, Node *dest) {
    if (src == NULL) {
        printf("Error occurred: source node is NULL\n");
        return;
    }
    if (dest == NULL) {
        printf("Error occurred: destination node is NULL\n");
        return;
    }

    Node *currentNode = src;
    while (currentNode->next != NULL) {
        currentNode = currentNode->next;
    }

    currentNode->next = dest;
}

void link_maze_edges(Maze *mazeGraph, int width, int height,
                     int maze[height][width]) {
    Directions directions[] = {LEFT, RIGHT, UP, DOWN};

    for (int i = 0; i < mazeGraph->num_of_nodes; i++) {
        Node *currentNode = mazeGraph->nodes[i];
        if (currentNode == NULL) {
            continue;
        }

        printf("\n\nSTARTING POINT NODE row %d column %d data %d",
               currentNode->row, currentNode->column, currentNode->data);

        for (int k = 0; k < 4; k++) {
            int new_row = currentNode->row;
            int new_column = currentNode->column;

            switch (directions[k]) {
            case LEFT:
                new_column--;
                printf("\n LEFT");
                break;
            case RIGHT:
                new_column++;
                printf("\n RIGHT");
                break;
            case UP:
                new_row--;
                printf("\n UP");
                break;
            case DOWN:
                new_row++;
                printf("\n DOWN");
                break;
            }

            // Check for out-of-bound coordinates
            if (new_row >= height || new_row < 0 || new_column >= width ||
                new_column < 0) {
                printf("\nSKIPPED THE DIRECTION new_row %d new_column %d",
                       new_row, new_column);
                continue;
            }

            printf("\nLOOKING FOR NODE AT row %d column %d", new_row,
                   new_column);

            // Search for the node with the new coordinates
            int found = 0;
            for (int j = 0; j < mazeGraph->num_of_nodes; j++) {
                Node *searchNode = mazeGraph->nodes[j];
                printf("\n CURRENT SEARCH row %d column %d", searchNode->row,
                       searchNode->column);
                if (searchNode->row == new_row &&
                    searchNode->column == new_column) {
                    printf("\nFOUND NODE AT row %d column %d", new_row,
                           new_column);
                    add_edge(currentNode, searchNode);
                    printf("\nEDGE ADDED BETWEEN row %d column %d AND row %d "
                           "column %d",
                           currentNode->row, currentNode->column, new_row,
                           new_column);
                    found = 1;
                    break; // Found the node, break the inner loop
                }
            }

            if (!found) {
                printf("\nNODE NOT FOUND FOR DIRECTION %d at row %d column %d",
                       directions[k], new_row, new_column);
            }
            printf("\n CONTINUE");
        }
        printf("\nLOOKED IN ALL DIRECTIONS");
    }

    printf("\nFinished linking all nodes.\n");
}

Maze *convert_to_graph(int width, int height, int maze[height][width]) {
    int num_of_nodes = 0;

    Node *rootNode = NULL;
    Node *currentNode = rootNode;
    Node *newNode = NULL;

    // creates a node for every element that is not a 1
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            if (maze[i][j] != 1) {
                newNode = create_node(maze[i][j], i, j);

                if (rootNode == NULL) {
                    rootNode = newNode;
                    currentNode = rootNode;
                } else {
                    currentNode->next = newNode;
                    currentNode = currentNode->next;
                }
                num_of_nodes++;
            }
        }
    }

    // adds all root nodes of linked lists to the maze graph
    currentNode = rootNode;
    Maze *mazeGraph = create_maze(width, height, num_of_nodes);

    for (int i = 0; i < num_of_nodes; i++) {
        if (currentNode == NULL) {
            break;
        }
        add_node(mazeGraph, currentNode, i);
        currentNode = currentNode->next;
    }

    // link the maze edges between numbers
    link_maze_edges(mazeGraph, width, height, maze);

    return mazeGraph;
}

void show_graph(Maze *maze) {
    int count = 0;
    while (true) {
        Node *currentNode = maze->nodes[count];

        if (currentNode == NULL) {
            break;
        }

        printf("\nNODE LIST (%d, %d)", currentNode->row, currentNode->column);

        while (true) {
            if (currentNode == NULL) {
                break;
            }

            printf(" -> (%d, %d)", currentNode->row, currentNode->column);
            currentNode = currentNode->next;
        }

        count++;
    }
}
