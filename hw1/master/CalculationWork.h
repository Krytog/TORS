#pragma once

#include <cstddef>

namespace calculations {
    
    struct ArgPack {
        double from;
        double to;
        double step;
        size_t iters_per_task;
    };

    double GetAnswer(const ArgPack& arg_pack);
}