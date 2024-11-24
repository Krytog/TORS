#include <common/Sockets.h>
#include <common/MessageBuffer.h>
#include <common/Messages.h>
#include <common/Constants.h>
#include <common/Task.h>

#include <worker/func.h>

#include <iostream>
#include <cstring>


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

double GetAnswer(double from, double to, double step) {
    double result = 0;
    for (double cur = from; cur < to; cur += step) {
        result += Function(cur) * step;
    }
    return result;
}

void ProcessTask(int socket) {
    char buffer[kBufferSize];
    memset(buffer, 0, kBufferSize);
    recv(socket, buffer, kBufferSize, 0);

    Task task;
    memcpy(&task, buffer, sizeof(task));

    std::cout << "GOT TASK: " << task.from << " " << task.to << " " << task.step << " " << task.index << std::endl;

    const double result = GetAnswer(task.from, task.to, task.step);
    Answer answer{
        .value = result,
        .index = task.index,
    };

    char message[sizeof(answer)];
    memcpy(message, &answer, sizeof(answer));
    send(socket, message, sizeof(answer), 0);
}

void Serve() {
    while (true) {
        TCPSocket socket; 
        socket.Bind(kWorkPort);
        socket.Listen();

        while (true) {
            int client_socket;
            socket.Accept(&client_socket);
            ProcessTask(client_socket);
        }
    }
}


void work() {
    RegisterAtMaster();
    Serve();
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
