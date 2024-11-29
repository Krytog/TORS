#pragma once

#include <unordered_set>
#include <arpa/inet.h>
#include <mutex>


class WorkersRegistry {
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

public:
    WorkersRegistry();

    void Add(const sockaddr_in& addr);

    void Remove(const sockaddr_in& addr);

    void RemoveUnsafe(const sockaddr_in& addr);

    bool DoesContain(const sockaddr_in& addr);

    const std::unordered_set<sockaddr_in, sockaddrhash, sockaddrequal>& GetRawSet() const;

    std::mutex& GetMutex();

private:
    std::unordered_set<sockaddr_in, sockaddrhash, sockaddrequal> registry_;
    std::mutex mutex_;
};
