from crdt.config import MY_ID
from crdt.crdt import CRDT_INSTANCE
from crdt.heartbeats import heartbeats_routine
from server.router import router

from common.logger import logger

from fastapi import FastAPI
import uvicorn
import threading
from os import environ


API_HOST = environ.get("API_HOST")
API_PORT = int(environ.get("API_PORT"))


class Server:
    def __init__(self):
        logger.info(f"Server {MY_ID} comes online")

        self.heartbeats_thread = None

        self.app = FastAPI()
        self.app.include_router(router)


    def run(self):
        self.heartbeats_thread = threading.Thread(target=heartbeats_routine, args=(CRDT_INSTANCE,), daemon=True)
        self.heartbeats_thread.start()
        uvicorn.run(self.app, host=API_HOST, port=API_PORT)        
