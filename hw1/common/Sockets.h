#pragma once

#include <arpa/inet.h>

#include <string>
#include <utility>


class Socket {
public:
    Socket(int type);

    int GetRawSocket() const;

    ~Socket();

protected:
    int fd_;
};


class UDPSocket : public Socket {
public:
    UDPSocket();

    void Send(const std::string& message, const struct sockaddr_in& dest) const;

    struct sockaddr_in Recieve(std::pair<std::string*, size_t*> dest) const;

    void Bind(int port) const;
};


class UDPBroadcastSocket : public UDPSocket {
public:
    UDPBroadcastSocket();


};
