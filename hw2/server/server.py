from server.grpc_server import grpc_server_routine
from server.router import router
from raft.elections import elections_routine
from raft.config import MY_ID
from raft.role_transitions import transit_to_follower
from raft.leader import leader_routine

from common.logging import logger

from fastapi import FastAPI
import uvicorn
import threading
from os import environ


API_HOST = environ.get("API_HOST")
API_PORT = int(environ.get("API_PORT"))


class Server:
    def __init__(self):
        logger.info(f"Server {MY_ID} comes online")
        transit_to_follower()

        self.grpc_server_thread = None
        self.elections_thread = None
        self.leader_thread = None

        self.app = FastAPI()
        self.app.include_router(router)

    def run(self):
        self.grpc_server_thread = threading.Thread(target=grpc_server_routine, daemon=True)
        self.elections_thread = threading.Thread(target=elections_routine, daemon=True)
        self.leader_thread = threading.Thread(target=leader_routine, daemon=True)

        self.grpc_server_thread.start()
        self.elections_thread.start()
        self.leader_thread.start()

        logger.info("All threads are running!")

        uvicorn.run(self.app, host=API_HOST, port=API_PORT)        
