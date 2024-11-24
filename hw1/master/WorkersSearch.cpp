#include "WorkersSearch.h"

#include <common/Messages.h>
#include <common/Address.h>
#include <common/MessageBuffer.h>
#include <common/Constants.h>

#include <signal.h>

#include <iostream>


namespace {
    UDPBroadcastSocket* broadcast_socket = nullptr;

    void on_alarm(int sig) {
        if (sig == SIGALRM) {
            if (!broadcast_socket) {
                std::cout << "Alarm fired, but socket is nullptr" << std::endl;
                return;
            }
            workersearch::Broadcast(*broadcast_socket);
            alarm(kBroadcastInterval);
        }
    }
}

namespace workersearch {

    void Broadcast(UDPBroadcastSocket& socket) {
        std::cout << "Broadcasting to find new workers" << std::endl;
        socket.Send(messages::kAcquaintanceMessageRequest, Address(INADDR_BROADCAST, kAcquaitancePort).Get());
    }

    void RegisterWorkers(UDPBroadcastSocket& socket, const bool* should_run, WorkersRegistry& registry) {
        MessageBuffer buffer(kBufferSize);
        while (*should_run) {
            const auto from = socket.Recieve(buffer.GetBufferForReading());
            if (buffer.GetMessage() == messages::kAcquaintanceMessageResponse) {
                std::cout << "Got acquaitance response from " << from.sin_addr.s_addr << std::endl;
                if (!registry.DoesContain(from)) {
                    struct sockaddr_in addr_for_tasks = from;
                    addr_for_tasks.sin_port = htons(kWorkPort);
                    registry.Add(addr_for_tasks);
                    std::cout << "Registered " << from.sin_addr.s_addr << std::endl;
                } else {
                    std::cout << "Got response from already registered worker" << std::endl;
                }
            } else {
                std::cout << "Recieved something strange: " << buffer.GetMessage() << std::endl;
            }
        }
    }

    void WorkerSearchRoutine(const bool* should_run, WorkersRegistry* registry) {
        UDPBroadcastSocket socket;
        broadcast_socket = &socket;

        signal(SIGALRM, on_alarm);

        Broadcast(socket);
        alarm(kBroadcastInterval);

        RegisterWorkers(socket, should_run, *registry);

        broadcast_socket = nullptr;
    }

}