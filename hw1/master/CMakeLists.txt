add_executable(master main.cpp)

target_include_directories(master PRIVATE ${BASE_PATH})
target_link_libraries(master PRIVATE common)
