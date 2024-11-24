#pragma once

#include <cmath>


inline double Function(double x) {
    x += 1;
    return std::sin(x) * std::log(x);
}
