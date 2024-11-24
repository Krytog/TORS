#include "Sockets.h"

#include <unistd.h>
#include <sys/socket.h>

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

void Socket::Send(const std::string& message, const sockaddr_in& dest) const {
    if (sendto(fd_, message.data(), message.size(), 0, (struct sockaddr*)&dest, sizeof(dest)) < 0) {
        throw std::runtime_error("Failed to send data via socket");
    }
}

struct sockaddr_in Socket::Recieve(std::pair<std::string*, size_t*> dest) const {
    auto [buffer, bytes_read] = dest;
    struct sockaddr_in from;
    socklen_t addr_len = sizeof(from);
    auto read = recvfrom(fd_, buffer->data(), buffer->size(), 0, (struct sockaddr*)&from, &addr_len);
    if (read < 0) {
        throw std::runtime_error("Failed to recieve data via socket");
    }
    *bytes_read = read;
    return from;
}

void Socket::Bind(int port) const {
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

TCPSocket::TCPSocket() : Socket(SOCK_STREAM) {
}

void TCPSocket::Listen() {
    constexpr int queue_size = 5;
    if (listen(fd_, queue_size) < 0) {
        throw std::runtime_error("Failed to listen on tcp socket");
    }
}

struct sockaddr_in TCPSocket::Accept(int* client_socket) {
    struct sockaddr_in addr;
    socklen_t addr_len = sizeof(addr);
    int sock = accept(fd_, (struct sockaddr*)&addr, &addr_len);
    if (sock < 0) {
        throw std::runtime_error("Failed to accept");
    }
    *client_socket = sock;
    return addr;
}

void TCPSocket::Connect(const struct sockaddr_in& dest) {
    if (connect(fd_, (struct sockaddr*)&dest, sizeof(dest)) < 0) {
        throw std::runtime_error("Failed to connect");
    }
}

TCPKeepAliveSocket::TCPKeepAliveSocket() {
    int optval = 1;
    if (setsockopt(fd_, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval)) < 0) {
        throw std::runtime_error("Failed to enable keepalive");
    }

    constexpr int keepalive_idle = 5;
    optval = keepalive_idle;
    if (setsockopt(fd_, IPPROTO_TCP, TCP_KEEPIDLE, &optval, sizeof(optval)) < 0) {
        throw std::runtime_error("Failed to set keepidle");
    }

    constexpr int keepalive_interval_probe = 3;
    optval = keepalive_interval_probe;
    if (setsockopt(fd_, IPPROTO_TCP, TCP_KEEPINTVL, &optval, sizeof(optval)) < 0) {
        throw std::runtime_error("Failed to set keepintvl");
    }

    constexpr int keepalive_probes_count = 3;
    optval = keepalive_probes_count;
    if (setsockopt(fd_, IPPROTO_TCP, TCP_KEEPCNT, &optval, sizeof(optval)) < 0) {
        throw std::runtime_error("Failed to set keepcnt");
    }
}
