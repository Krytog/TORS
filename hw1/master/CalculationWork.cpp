#include "CalculationWork.h"

#include <master/WorkersRegistry.h>

#include <common/Task.h>
#include <common/Sockets.h>
#include <common/MessageBuffer.h>
#include <common/Constants.h>

#include <queue>
#include <stdexcept>
#include <sys/epoll.h>
#include <algorithm>
#include <unordered_map>
#include <cstring>
#include <iostream>
#include <thread>
#include <chrono>


const int kMaxEpollEvents = 256;
const int kMaxEpollWaitTime = 10000; // in milliseconds


namespace {
    struct sockaddrhash {
    public:
        size_t operator()(const sockaddr_in& sock) const {
            return std::hash<uint32_t>()(sock.sin_addr.s_addr);
        }
    };

    struct sockaddrequal {
    public:
        bool operator()(const sockaddr_in& lhs, const sockaddr_in& rhs) const {
            return lhs.sin_addr.s_addr == rhs.sin_addr.s_addr;
        }
    };

    std::mutex* mutex_;
    std::unordered_map<int, sockaddr_in> fd_to_servers;
    std::unordered_map<sockaddr_in, TCPKeepAliveSocket, sockaddrhash, sockaddrequal> servers_to_sockets;
    std::unordered_map<sockaddr_in, Task, sockaddrhash, sockaddrequal> servers_to_tasks;
    std::unordered_map<size_t, double> ready;


    std::queue<Task> GetTasksQueue(size_t iters_per_task, const calculations::ArgPack& arg_pack) {
        std::queue<Task> queue;
        double current = arg_pack.from;
        size_t index = 0;
        while (current < arg_pack.to) {
            double to = current + arg_pack.step * iters_per_task;
            to = std::min(to, arg_pack.to);
            queue.push(Task{current, to, arg_pack.step, index});
            current = to;
            ++index;
        }
        return queue;
    }

    void ProcessSocketEvent(int fd) {
        std::lock_guard lock(*mutex_);      

        MessageBuffer buffer(kBufferSize);
        try {
            sock->Recieve(buffer.GetBufferForReading());
            const std::string message = buffer.GetMessage();

            Answer answer;
            std::memcpy((void*)&answer, message.data(), message.size());

            if (!ready.contains(answer.index)) {
                std::cout << "Got answer to task " << answer.index << ". The value is " << answer.value << std::endl;
                ready[answer.index] = answer.value;
            }

            std::lock_guard lock(mappings_mutex_);
            is_server_busy[server] = false;

        } catch (std::runtime_error& error) {
            std::cout << "Found dead server: " << server.sin_addr.s_addr << std::endl;
            std::lock_guard lock(mappings_mutex_);
            is_server_busy.erase(server);
            fd_to_servers.erase(fd);
        }
    }

    void EpollWorker(int epoll_fd, const bool* should_run) {
        struct epoll_event events[kMaxEpollEvents];

        while (*should_run) {
            int events_count = epoll_wait(epoll_fd, events, kMaxEpollEvents, kMaxEpollWaitTime);
            if (events_count < 0) {
                throw std::runtime_error("Failed to wait on epoll");
            }

            for (int i = 0; i < events_count; ++i) {
                int fd = events[i].data.fd;
                if (events[i].events & EPOLLIN) {
                    ProcessSocketEvent(fd);
                }
            }
        }
    }

    void SendTaskToServer(const sockaddr_in& server, const Task& task, int epoll_fd) {
        servers_to_sockets[server] = TCPKeepAliveSocket();
        TCPKeepAliveSocket& socket = servers_to_sockets[server];

        socket.Connect(server);

        struct epoll_event ev;
        ev.events = EPOLLIN;
        ev.data.fd = socket.GetRawSocket();

        if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, socket.GetRawSocket(), &ev) == -1) {
            throw std::runtime_error("Failed to add event to epoll");
        }
    }
}


namespace calculations {

    double GetAnswer(const ArgPack& arg_pack, size_t iters_per_task, WorkersRegistry* registry) {
        if (arg_pack.from > arg_pack.to) {
            throw std::runtime_error("Invalid params: from > to");
        }

        int epoll_fd;


        std::queue<Task> tasks = GetTasksQueue(iters_per_task, arg_pack);
        while (!tasks.empty()) {
            const auto task = tasks.front();
            tasks.pop();

            bool assigned = false;
            std::lock_guard lock(registry->GetMutex());
            for (const auto& server : registry->GetRawSet()) {
                if (servers_to_sockets.contains(server)) {
                    continue;
                }

                try {
                    SendTaskToServer(server, task, epoll_fd);
                    assigned = true;
                    servers_to_tasks[server] = task;
                    break;
                } catch (std::runtime_error& error) {
                    std::cout << "Eror when assigning task " << error.what() << std::endl;
                }
            }

            if (!assigned) {
                tasks.push(task);
                std::cout << "Failed to assign task to whomever, backoff" << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(500)); // backoff
            }
        }
    }

};
