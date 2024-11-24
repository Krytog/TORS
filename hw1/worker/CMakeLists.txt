add_executable(worker main.cpp)

target_include_directories(worker PRIVATE ${BASE_PATH})
target_link_libraries(worker PRIVATE common)
