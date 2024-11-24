#pragma once

#include <arpa/inet.h>

#include <string>
#include <utility>


class Socket {
public:
    Socket(int type);

    int GetRawSocket() const;

    ~Socket();

    void Send(const std::string& message, const struct sockaddr_in& dest) const;

    struct sockaddr_in Recieve(std::pair<std::string*, size_t*> dest) const;

    void Bind(int port) const;

protected:
    int fd_;
};


class UDPSocket : public Socket {
public:
    UDPSocket();
};

class UDPBroadcastSocket : public UDPSocket {
public:
    UDPBroadcastSocket();


};

class TCPSocket : public Socket {
public:
    TCPSocket();

    void Connect(const struct sockaddr_in& dest);

    void Listen();

    struct sockaddr_in Accept(int* client_socket);
};

class TCPKeepAliveSocket : public TCPSocket {
public:
    TCPKeepAliveSocket();
};
