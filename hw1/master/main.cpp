#include <common/Sockets.h>
#include <common/Address.h>
#include <common/Messages.h>

#include <iostream>


const int kAcquaitancePort = 31337;


void work() {
    UDPBroadcastSocket socket;

    socket.Send(messages::kAcquaintanceMessageRequest, Address(INADDR_BROADCAST, kAcquaitancePort).Get());
}

int main() {
    std::cout << "Master started" << std::endl;
    try {
        work();
    } catch (std::runtime_error& error)  {
        std::cout << "Something went wrong: " << error.what() << std::endl;
    }
    std::cout << "Master finished" << std::endl;
    return 0;
}
