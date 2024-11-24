#include <common/Sockets.h>
#include <common/MessageBuffer.h>
#include <common/Messages.h>

#include <iostream>


const int kAcquaitancePort = 31337;
const size_t kBufferSize = 1024;


void RegisterAtMaster() {
    UDPSocket socket;
    socket.Bind(kAcquaitancePort);

    MessageBuffer buffer(kBufferSize);
    const auto sender_addr = socket.Recieve(buffer.GetBufferForReading());
    std::cout << "MASTER ADDRESS IS " << sender_addr.sin_addr.s_addr << std::endl;
    std::cout << "MASTER PORT IS " << sender_addr.sin_port << std::endl;
    if (buffer.GetMessage() != messages::kAcquaintanceMessageRequest) {
        std::cout << buffer.GetMessage() << std::endl;
        throw std::runtime_error("Recieved unexpected message on broadcast port");
    }

    socket.Send(messages::kAcquaintanceMessageResponse, sender_addr);
}


void work() {
    RegisterAtMaster();
}


int main() {
    std::cout << "Worker started" << std::endl;
    try {
        work();
    } catch (std::runtime_error& error)  {
        std::cout << "Something went wrong: " << error.what() << std::endl;
    }
    std::cout << "Worker finished" << std::endl;
    return 0;
}
