#include "Address.h"

Address::Address(in_addr_t addr, int port) {
    inner_addr_.sin_family = AF_INET;
    inner_addr_.sin_port = port;
    inner_addr_.sin_addr.s_addr = addr;
}

sockaddr_in Address::Get() const {
    return inner_addr_;
}
