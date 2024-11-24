#pragma once

#include <arpa/inet.h>


class Address {
public:
    Address(in_addr_t addr, int port);

    sockaddr_in Get() const;

private:
    sockaddr_in inner_addr_;
};
