#pragma once

#include <string>
#include <utility>


class MessageBuffer {
public:
    MessageBuffer(size_t buffer_size);

    std::pair<std::string*, size_t*> GetBufferForReading();

    std::string GetMessage() const;

private:
    std::string buffer_;
    size_t message_size_{0};
};
