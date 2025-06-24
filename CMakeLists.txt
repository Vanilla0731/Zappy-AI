##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## CMakeLists.txt
##

cmake_minimum_required(VERSION 3.16)
project(zappy_ai VERSION 1.0)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O3")
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE ON)

########################################
# INFO: enable multithreading for build
########################################
include(ProcessorCount)
ProcessorCount(N)
if(NOT N EQUAL 0)
    set(CMAKE_BUILD_PARALLEL_LEVEL ${N})
endif()

########################################
# INFO: CMake cache management for faster builds
########################################
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

file(GLOB MAIN_SOURCE CONFIGURE_DEPENDS
    "${CMAKE_CURRENT_SOURCE_DIR}/src/exec/exec.c")

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|AppleClang")
    file(GLOB PATH_SOURCE CONFIGURE_DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/src/exec/get_macos_path.c")
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    file(GLOB PATH_SOURCE CONFIGURE_DEPENDS
        "${CMAKE_CURRENT_SOURCE_DIR}/src/exec/get_linux_path.c")
endif()

########################################
# NOTE: Zappy AI client
########################################
add_executable(zappy_ai
    ${MAIN_SOURCE}
    ${PATH_SOURCE}
)

target_compile_options(zappy_ai PRIVATE
    # INFO: classic warnings
    -Wall
    -Wextra
    -Werror
    -pedantic

    # INFO: type safety & conversions
    -Wconversion
    -Wsign-conversion
    -Wfloat-equal

    # INFO: code correctness
    -Wshadow
    -Wnull-dereference
    -Wundef
    -Wuninitialized
    -Winit-self
    -Wredundant-decls

    # INFO: code hygiene
    -Wcast-align
    -Wcast-qual
    -Wmissing-declarations

    # INFO: logic bugs & bad practices
    -Wswitch-default
    -Wswitch-enum

    # INFO: prevent common portability issues
    -Wdouble-promotion
    -Wwrite-strings

    # INFO: disabling this because this causes a compilation error
    -Wno-gnu-zero-variadic-macro-arguments
)

if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(zappy_ai PRIVATE -Wno-format-truncation)
endif()

########################################
# NOTE: debug
########################################
option(ZAP_AI_ENABLE_DEBUG "Enable debug definition" OFF)

if(ENABLE_DEBUG)
    target_compile_definitions(zappy_gui PRIVATE DEBUG=1)
endif()
