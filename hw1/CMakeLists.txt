cmake_minimum_required(VERSION 3.16)
project(hw1 CXX)

set(CMAKE_CXX_STANDARD 20)

set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

SET(BASE_PATH "${CMAKE_SOURCE_DIR}")

add_subdirectory(common)
add_subdirectory(master)
add_subdirectory(worker)
