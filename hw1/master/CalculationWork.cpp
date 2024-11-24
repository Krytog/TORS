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
#include <mutex>


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
    std::unordered_map<size_t, double> results;
    std::queue<Task> tasks; 


    std::queue<Task> GetTasksQueue(const calculations::ArgPack& arg_pack) {
        std::queue<Task> queue;
        double current = arg_pack.from;
        size_t index = 0;
        while (current < arg_pack.to) {
            double to = current + arg_pack.step * arg_pack.iters_per_task;
            to = std::min(to, arg_pack.to);
            queue.push(Task{current, to, arg_pack.step, index});
            current = to;
            ++index;
        }
        return queue;
    }

    void ClearMappings(const sockaddr_in& server, int fd) {
        servers_to_tasks.erase(server);
        servers_to_sockets.erase(server);
        fd_to_servers.erase(fd);
    }

    void ProcessSocketEvent(int fd) {
        std::lock_guard lock(*mutex_);
        const sockaddr_in& server = fd_to_servers.at(fd);
        TCPKeepAliveSocket* sock = &servers_to_sockets.at(server);


        MessageBuffer buffer(kBufferSize);
        try {
            sock->Recieve(buffer.GetBufferForReading());
            const std::string message = buffer.GetMessage();

            Answer answer;
            std::memcpy((void*)&answer, message.data(), message.size());

            if (!results.contains(answer.index)) {
                std::cout << "Got answer to task " << answer.index << ". The value is " << answer.value << std::endl;
                results[answer.index] = answer.value;
            }

        } catch (std::runtime_error& error) {
            std::cout << "Found dead server: " << server.sin_addr.s_addr << std::endl;
            std::cout << "Returning task with index " << servers_to_tasks[server].index << " to the tasks queue" << std::endl;
            
            tasks.push(servers_to_tasks[server]);
        }

        ClearMappings(server, fd);
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
        servers_to_sockets.emplace(std::piecewise_construct, std::forward_as_tuple(server), std::forward_as_tuple()); // we can't move
        TCPKeepAliveSocket& sock = servers_to_sockets[server];
        
        sock.Connect(server);

        struct epoll_event ev;
        ev.events = EPOLLIN;
        ev.data.fd = sock.GetRawSocket();

        if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sock.GetRawSocket(), &ev) == -1) {
            throw std::runtime_error("Failed to add event to epoll");
        }

        std::string message;
        message.resize(sizeof(task));
        memcpy(message.data(), &task, sizeof(task));
        send(sock.GetRawSocket(), message.data(), message.size(), 0);
    }

    void InitGlobals(const calculations::ArgPack& arg_pack, WorkersRegistry* registry) {
        mutex_ = &registry->GetMutex();
        tasks = GetTasksQueue(arg_pack);
    }

    double CalculateResultingValue() {
        double result = 0;
        for (const auto [_, value] : results) {
            result += value;
        }
        return result;
    }

    int GetEpoll() {
        int epoll_fd = epoll_create1(0);
        if (epoll_fd == -1) {
            throw std::runtime_error("Failed to create epoll");
        }
        return epoll_fd;
    }
}


namespace calculations {

    double GetAnswer(const ArgPack& arg_pack, WorkersRegistry* registry) {
        InitGlobals(arg_pack, registry);

        int epoll_fd = GetEpoll();
        bool should_run = true;
        std::thread epoll_worker(EpollWorker, epoll_fd, &should_run);
        
        const size_t tasks_count = tasks.size();
        std::cout << "Calculation will take " << tasks_count << " tasks" << std::endl;
        while (true) {
            std::unique_lock lock(registry->GetMutex());

            if (results.size() == tasks_count) {
                break;
            }

            const auto task = tasks.front();
            tasks.pop();

            bool assigned = false;
            for (const auto& server : registry->GetRawSet()) {
                if (servers_to_tasks.contains(server)) {
                    continue;
                }

                try {
                    SendTaskToServer(server, task, epoll_fd);
                    assigned = true;
                    servers_to_tasks[server] = task;
                    fd_to_servers[servers_to_sockets.at(server).GetRawSocket()] = server;
                    break;
                } catch (std::runtime_error& error) {
                    std::cout << "Eror when assigning task " << error.what() << std::endl;
                }
            }

            if (!assigned) {
                tasks.push(task);
                lock.unlock(); 
                std::cout << "Failed to assign task to whomever, backoff" << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(5000)); // backoff
            }
        }

        should_run = false;
        epoll_worker.join();

        const double result = CalculateResultingValue();
        return result;
    }

};
