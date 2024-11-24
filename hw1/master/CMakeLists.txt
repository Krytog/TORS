add_executable(master 
    main.cpp
    WorkersSearch.cpp
    WorkersRegistry.cpp
    CalculationWork.cpp
)

target_include_directories(master PRIVATE ${BASE_PATH})
target_link_libraries(master PRIVATE common)
