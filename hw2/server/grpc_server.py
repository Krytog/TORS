from raft.grpc_impl import RaftGRPC
from raft.config import CONFIG, MY_ID

from common.logging import logger

from proto import raft_pb2_grpc

import grpc
import asyncio
from concurrent import futures


async def run_grpc_server():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=8))
    raft_pb2_grpc.add_RaftServicer_to_server(RaftGRPC(), server)

    my_id = str(MY_ID)
    server.add_insecure_port(CONFIG[my_id][0] + ":" + CONFIG[my_id][1])

    await server.start()
    logger.info(f"gRPC service of server {MY_ID} has started")
    await server.wait_for_termination()


def grpc_server_routine():
    asyncio.run(run_grpc_server())
