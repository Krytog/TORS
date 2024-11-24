#pragma once

#include <master/WorkersRegistry.h>

#include <common/Sockets.h>


namespace workersearch {

    void Broadcast(UDPBroadcastSocket& socket);

    void RegisterWorkers(UDPBroadcastSocket& socket, const bool* should_run, WorkersRegistry& registry);

    void WorkerSearchRoutine(const bool* should_run, WorkersRegistry* registry);

};
