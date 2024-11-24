#include "Sockets.h"

#include <unistd.h>

#include <stdexcept>


Socket::Socket(int type) {
    fd_ = socket(AF_INET, type, 0);
    if (fd_ == -1) {
        throw std::runtime_error("Failed to create socket");
    }
}

int Socket::GetRawSocket() const {
    return fd_;
}

Socket::~Socket() {
    close(fd_);
}


UDPSocket::UDPSocket() : Socket(SOCK_DGRAM) {
}

void UDPSocket::Send(const std::string& message, const sockaddr_in& dest) const {
    if (sendto(fd_, message.data(), message.size(), 0, (struct sockaddr*)&dest, sizeof(dest)) < 0) {
        throw std::runtime_error("Failed to send data via UDP socket");
    }
}

struct sockaddr_in UDPSocket::Recieve(std::pair<std::string*, size_t*> dest) const {
    auto [buffer, bytes_read] = dest;
    struct sockaddr_in from;
    socklen_t addr_len = sizeof(from);
    auto read = recvfrom(fd_, buffer->data(), buffer->size(), 0, (struct sockaddr*)&from, &addr_len);
    if (read < 0) {
        throw std::runtime_error("Failed to recieve data via UDP socket");
    }
    *bytes_read = read;
    return from;
}

void UDPSocket::Bind(int port) const {
    struct sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);
    if (bind(fd_, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        throw std::runtime_error("Failed to bind socket");
    }
}


UDPBroadcastSocket::UDPBroadcastSocket() {
    int broadcast = 1;
    if (setsockopt(fd_, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
        throw std::runtime_error("Failed to enable broadcast");
    }
}
