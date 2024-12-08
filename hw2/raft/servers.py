from proto import raft_pb2, raft_pb2_grpc
from raft.config import CONFIG, MY_ID

import grpc


class ServerMaster:
    def __init__(self):
        self.channels = {}
        self.servers = {}
        for server_id, server_params in CONFIG.items():
            server = int(server_id)
            server_addr, server_port = server_params[0], server_params[1]
            if server != MY_ID:
                self.channels[server] = grpc.insecure_channel(server_addr + ":" + server_port)
                self.servers[server] = raft_pb2_grpc.RaftStub(self.channels[server])


SERVER_MASTER = ServerMaster()
