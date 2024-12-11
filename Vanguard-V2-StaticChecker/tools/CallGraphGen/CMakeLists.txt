add_library(cg SHARED gen.cpp)

# specify the libs that the target 'cg' needs
# !!! DO NOT change the order of the libs !!!
# libs will be linked in this order, and changing the order could lead to link errors
target_link_libraries(cg
    framework
    json
    ${CLANG_LIBS}
    ${LLVM_LIBS}
    ${OTHER_LIBS}
    )

add_executable(cge gen.cpp)

# specify the libs that the target 'cg' needs
# !!! DO NOT change the order of the libs !!!
# libs will be linked in this order, and changing the order could lead to link errors
target_link_libraries(cge
        framework
        json
        ${CLANG_LIBS}
        ${LLVM_LIBS}
        ${OTHER_LIBS}
        )

