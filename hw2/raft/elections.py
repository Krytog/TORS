from raft.config import CONFIG, MY_ID
from raft.servers import SERVER_MASTER
from raft.state import STATE
from raft.status import STATUS_HOLDER, Status
from raft.timings import TIMING
import raft.role_transitions as role_transitions

from proto import raft_pb2

from common.logging import logger
from threading import Lock
from time import time, sleep
import concurrent


class Elections:
    def __init__(self):
        self.__count = 0
        self.__needed = len(CONFIG) // 2 + 1
        self.is_in_process = False
        self.mutex = Lock()

    def has_enough_votes(self):
        return self.__count >= self.__needed
    
    def handle_new_vote(self):
        self.__count += 1
        with self.mutex:
            if self.has_enough_votes() and self.is_in_process:
                self.__count = 0
                ELECTIONS.is_in_process = False
                role_transitions.transit_to_leader()

    def is_in_process_safe(self):
        with self.mutex:
            return self.is_in_process
        
    def set_is_in_process_safe(self, value):
        with self.mutex:
            self.is_in_process = value

    def reset_count(self):
        self.__count = 0

    def add_vote(self):
        self.__count += 1


ELECTIONS = Elections()

VOTE_WAITING_TIMEOUT = 1
ELECTIONS_WAITING_TIMEOUT = 30


def vote_task(grpc_stub):
    try:
        response = grpc_stub.AskVote(
            raft_pb2.VoteRequest(
                term=STATE.term,
                candidate_id=MY_ID,
                log_last_term=STATE.log[-1].term,
                log_last_index=len(STATE.log) - 1
            ),
            timeout=VOTE_WAITING_TIMEOUT
        )
        TIMING.set_new_last_action_timestamp_safe(time())

        print("Response:", response.term, response.is_vote_granted, flush=True)

        if response.term > STATE.term:
            STATE.update_if_stale(response.term)
            ELECTIONS.set_is_in_process_safe(False)
            role_transitions.transit_to_follower()

        if response.is_vote_granted:
            ELECTIONS.handle_new_vote()

    except Exception as err:
        logger.debug(f"Something went wrong inside vote task. What: {str(err)}")


def elections():
    ELECTIONS.reset_count()
    STATE.term += 1
    STATE.leader_id = 0
    
    # voting for ourself
    STATE.voted_for = MY_ID 
    ELECTIONS.add_vote()

    role_transitions.transit_to_candidate()
    logger.info(f"Elections for term {STATE.term} from server {MY_ID} are started")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = set()
        for _, grpc_stub in SERVER_MASTER.servers.items():
            futures.add(executor.submit(vote_task, grpc_stub))

        try:
            for _ in concurrent.futures.as_completed(futures, timeout=ELECTIONS_WAITING_TIMEOUT):
                if not ELECTIONS.is_in_process_safe():
                    for unfinished_future in futures:
                        unfinished_future.cancel()
                    break

        except Exception as err:
            logger.error(f"Something went wrong during the elections. What: {str(err)}")
    
    ELECTIONS.set_is_in_process_safe(False)


def elections_routine():
    sleep(3)
    while True:
        if TIMING.should_start_elections() and STATUS_HOLDER.status != Status.Leader:
            logger.info(f"Server {MY_ID} timeouts and starts new elections")
            ELECTIONS.set_is_in_process_safe(True)
            elections()
            TIMING.set_new_random_timeout()
            TIMING.set_new_last_action_timestamp_safe(time())
