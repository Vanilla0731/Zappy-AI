cmake_minimum_required(VERSION 3.16)
project(zappy_ai VERSION 1.0)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O3")

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

option(ZAP_AI_ENABLE_DEBUG "Enable debug definition" OFF)

if(ZAP_AI_ENABLE_DEBUG)
    target_compile_definitions(zappy_ai PRIVATE CEXTEND_DEBUG=1)
endif()

########################################

file(GLOB TEST_SOURCE
    "tests/*.c")

add_executable(zap_srv_unit_tests
    ${TEST_SOURCE}
    ${MAIN_SOURCE}
    ${PATH_SOURCE}
)

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|AppleClang")
    target_compile_options(zap_srv_unit_tests PRIVATE -fprofile-instr-generate -fcoverage-mapping)
    target_link_options(zap_srv_unit_tests PRIVATE -fprofile-instr-generate -fcoverage-mapping)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(zap_srv_unit_tests PRIVATE -fprofile-arcs -ftest-coverage)
    target_link_options(zap_srv_unit_tests PRIVATE -fprofile-arcs -ftest-coverage)
endif()

target_compile_definitions(zap_srv_unit_tests PRIVATE UNIT_TESTS=1)

target_link_libraries(zap_srv_unit_tests PRIVATE criterion sfml-graphics sfml-system sfml-window, cextend)

target_include_directories(zap_srv_unit_tests PRIVATE
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/external/lib-cextend/include>
)

enable_testing()
add_test(NAME zap_srv_unit_tests COMMAND zap_srv_unit_tests)

add_custom_target(zap_srv_tests_run
    COMMAND zap_srv_unit_tests
    DEPENDS zap_srv_unit_tests
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)
