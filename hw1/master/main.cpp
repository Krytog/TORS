#include <common/Sockets.h>
#include <common/Address.h>
#include <common/Messages.h>
#include <common/MessageBuffer.h>

#include <iostream>


const int kAcquaitancePort = 31337;
const size_t kBufferSize = 1024;


void work() {
    UDPBroadcastSocket socket;

    socket.Send(messages::kAcquaintanceMessageRequest, Address(INADDR_BROADCAST, kAcquaitancePort).Get());

    while (true) {
        MessageBuffer buffer(kBufferSize);
        const auto from = socket.Recieve(buffer.GetBufferForReading());

        std::cout << "GOT ANSWER " << buffer.GetMessage() << std::endl;
        std::cout << "FROM " << from.sin_addr.s_addr << std::endl;
    }
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
