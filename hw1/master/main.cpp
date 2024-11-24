#include <master/WorkersRegistry.h>
#include <master/WorkersSearch.h>

#include <thread>
#include <iostream>


void work() {
    WorkersRegistry registry;
    bool should_run = true;

    std::thread workers_seacher = std::thread(workersearch::WorkerSearchRoutine, &should_run, &registry);

    for (int i = 0; i < 999999999; ++i) {

    }

    should_run = false;
    workers_seacher.join();
}

int main() {
    std::cout << "Master started" << std::endl;
    try {
        work();
    } catch (std::runtime_error& error)  {
        std::cout << "Something went wrong: " << error.what() << std::endl;
    }
    std::cout << "Master finished" << std::endl;
    return 0;
}
