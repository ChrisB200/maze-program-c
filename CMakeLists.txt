cmake_minimum_required(VERSION 3.10)
project(MazeLibrary C)

# Set the C compiler
set(CMAKE_C_COMPILER gcc)

# Set the architecture to 64-bit
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -m64")

# Set the include directory
include_directories(${CMAKE_SOURCE_DIR}/include)

# Source files
set(SRC
    src/maze.c
    src/maze-generator.c
)

# Output directory for shared libraries
set(LIBRARY_OUTPUT_PATH ${CMAKE_SOURCE_DIR}/lib)

# Create shared libraries
add_library(maze-generator SHARED src/maze-generator.c src/maze.c)
add_library(maze-solver SHARED src/maze-solver.c src/maze.c)

# Specify the output locations for the shared libraries
set_target_properties(maze-generator PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${LIBRARY_OUTPUT_PATH}
    OUTPUT_NAME "maze-generator"
)

set_target_properties(maze-solver PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${LIBRARY_OUTPUT_PATH}
    OUTPUT_NAME "maze-solver"
)

# Clean target to remove generated files
add_custom_target(clean-all
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_SOURCE_DIR}/cmake_clean.cmake
)

# Create a custom CMake script for the clean-all target
file(WRITE ${CMAKE_SOURCE_DIR}/cmake_clean.cmake "
    file(GLOB_RECURSE GENERATED_FILES
        \"${CMAKE_SOURCE_DIR}/lib/*\"
        \"${CMAKE_BINARY_DIR}/*\"
    )
    foreach(FILE IN LISTS GENERATED_FILES)
        file(REMOVE \${FILE})
    endforeach()
")
