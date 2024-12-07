from proto import raft_pb2, raft_pb2_grpc
from raft.config import CONFIG, MY_ID

import grpc


CHANNELS = {}
SERVERS = {}
for server_id, server_params in CONFIG.items():
    server = int(server_id)
    server_addr, server_port = server_params[0], server_params[1]
    if server != MY_ID:
        CHANNELS[server] = grpc.insecure_channel(server_addr + ":" + server_port)
        SERVERS[server] = raft_pb2_grpc.RaftStub(CHANNELS[server])
