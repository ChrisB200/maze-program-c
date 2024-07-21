# Compiler
CC = gcc

# Flags
CFLAGS = -I./include -fPIC

# Source files
SRC = src/maze.c src/maze-generator.c src/maze-solver.c

# Object files
OBJ = $(SRC:.c=.o)

# Shared object files
GENERATOR_SO = lib/maze-generator.so
SOLVER_SO = lib/maze-solver.so

# Directories
LIB_DIR = lib

# Default target to build the shared objects
all: $(LIB_DIR) $(GENERATOR_SO) $(SOLVER_SO)

# Create lib directory if it does not exist
$(LIB_DIR):
	mkdir -p $(LIB_DIR)

# Rule to build maze-generator.so
$(GENERATOR_SO): src/maze-generator.o src/maze.o
	$(CC) -shared -o $@ $^ $(CFLAGS)

# Rule to build maze-solver.so
$(SOLVER_SO): src/maze-solver.o src/maze.o
	$(CC) -shared -o $@ $^ $(CFLAGS)

# General rule to compile source files into object files
%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)

# Clean target to remove generated files
clean:
	rm -f $(OBJ) $(GENERATOR_SO) $(SOLVER_SO)

.PHONY: all clean

