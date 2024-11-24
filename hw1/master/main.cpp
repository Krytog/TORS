#include <master/WorkersRegistry.h>
#include <master/WorkersSearch.h>
#include <master/CalculationWork.h>

#include <stdlib.h>
#include <thread>
#include <iostream>


void work(double from, double to, double step, size_t iters) {
    WorkersRegistry registry;
    bool should_run = true;

    std::thread workers_seacher = std::thread(workersearch::WorkerSearchRoutine, &should_run, &registry);

    calculations::ArgPack arg_pack{
        .from = from,
        .to = to,
        .step = step,
        .iters_per_task = iters,
    };

    const auto result = calculations::GetAnswer(arg_pack, &registry);
    std::cout << "The integral equals to " << result << std::endl;

    should_run = false;
    workers_seacher.join();
}

int main(int argc, char** argv) {
    std::cout << "Master started" << std::endl;
    try {
        double from = atof(argv[1]);
        double to = atof(argv[2]);
        double step = atof(argv[3]);
        size_t iters = atoll(argv[4]);

        std::cout << "Will count integral with given params: " << from << " "
        << to << " " << step << " " << iters << std::endl;

        work(from, to, step, iters);
    } catch (std::runtime_error& error)  {
        std::cout << "Something went wrong: " << error.what() << std::endl;
    }
    std::cout << "Master finished" << std::endl;
    return 0;
}
