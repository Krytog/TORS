#pragma once

#include <cstddef>

struct Task {
    double from;
    double to;
    double step;
    size_t index;
};

struct Answer {
    double value;
    size_t index;
};
