
    file(GLOB_RECURSE GENERATED_FILES
        "/home/chris/code/maze-program-c/lib/*"
        "/home/chris/code/maze-program-c/build/*"
    )
    foreach(FILE IN LISTS GENERATED_FILES)
        file(REMOVE ${FILE})
    endforeach()
