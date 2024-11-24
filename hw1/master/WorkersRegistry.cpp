#include "WorkersRegistry.h"

WorkersRegistry::WorkersRegistry() = default;

void WorkersRegistry::Add(const sockaddr_in& addr) {
    std::lock_guard lock(mutex_);
    registry_.insert(addr);
}

void WorkersRegistry::Remove(const sockaddr_in& addr) {
    std::lock_guard lock(mutex_);
    registry_.erase(addr);
}

bool WorkersRegistry::DoesContain(const sockaddr_in& addr) {
    return registry_.contains(addr);
}

const std::unordered_set<sockaddr_in, WorkersRegistry::sockaddrhash, WorkersRegistry::sockaddrequal>& WorkersRegistry::GetRawSet() const {
    return registry_;
}

std::mutex& WorkersRegistry::GetMutex() {
    return mutex_;
}
