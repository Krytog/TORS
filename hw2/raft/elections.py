from raft.config import CONFIG, MY_ID
from raft.servers import ServerAsyncMaster
from raft.state import STATE
from raft.timings import TIMING
import raft.role_transitions as role_transitions

from proto import raft_pb2

import asyncio
from common.logging import logger
from threading import Lock
from time import time, sleep


# SERVER_ASYNC_MASTER = None


class Elections:
    def __init__(self):
        self.__count = 0
        self.__needed = len(CONFIG) / 2 + 1
        self.is_in_process = False
        self.mutex = Lock()

    def has_enough_votes(self):
        return self.__count >= self.__needed
    
    def handle_new_vote(self):
        self.__count += 1
        with self.mutex:
            if self.__has_enough_votes() and self.is_in_process:
                self.__count = 0
                self.is_in_process = False
                role_transitions.transit_to_leader()

    def is_in_process_safe(self):
        with self.mutex:
            return self.is_in_process
        
    def set_is_in_process_safe(self, value):
        with self.mutex:
            self.is_in_process = value


ELECTIONS = Elections()

VOTE_WAITING_TIMEOUT = 0.1


async def vote_task(grpc_stub):
    try:
        response = await grpc_stub.AskVote(
            raft_pb2.VoteRequest(
                term=STATE.term,
                candidate_id=MY_ID,
                log_last_term=STATE.log[-1].term,
                log_last_index=len(STATE.log) - 1
            )
        )
        if response.is_vote_granted:
            TIMING.set_new_last_action_timestamp_safe(time())
            ELECTIONS.handle_new_vote()

    except Exception as err:
        logger.error(f"Something went wrong inside vote task: What: {str(err)}")


async def elections():
    STATE.term += 1
    logger.info(f"Elections for term {STATE.term} from server {MY_ID} are started")

    SERVER_ASYNC_MASTER = ServerAsyncMaster()
    tasks = set()
    for _, grpc_stub in SERVER_ASYNC_MASTER.servers.items():
        tasks.add(asyncio.create_task(vote_task(grpc_stub)))

    while ELECTIONS.is_in_process_safe() and len(tasks) > 0:
        _, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=VOTE_WAITING_TIMEOUT)

    ELECTIONS.set_is_in_process_safe(False)


def init_server_async_master():
    pass#global SERVER_ASYNC_MASTER
    #SERVER_ASYNC_MASTER = ServerAsyncMaster()


def elections_routine():
    asyncio.run(elections_routine_inner())


async def elections_routine_inner():
    sleep(3)
    init_server_async_master()
    while True:
        if TIMING.should_start_elections():
            logger.info(f"Server {MY_ID} timeouts and starts new elections")
            ELECTIONS.set_is_in_process_safe(True)
            await elections()
