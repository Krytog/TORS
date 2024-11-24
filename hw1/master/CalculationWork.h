#pragma once

namespace calculations {
    
    struct ArgPack {
        double from;
        double to;
        double step;
    };

    double GetAnswer(const ArgPack& arg_pack);
}