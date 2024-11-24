#include "MessageBuffer.h"

#include <string.h>

MessageBuffer::MessageBuffer(size_t buffer_size) {
    buffer_.resize(buffer_size);
}

std::pair<std::string*, size_t*> MessageBuffer::GetBufferForReading() {
    memset(buffer_.data(), 0, buffer_.size());
    return {&buffer_, &message_size_};
}

std::string MessageBuffer::GetMessage() const {
    return buffer_.substr(0, message_size_);
}
