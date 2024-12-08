from raft.status import STATUS_HOLDER, Status
from raft.state import STATE, LEADER_STATE
from raft.servers import SERVER_MASTER
from raft.config import MY_ID

from proto import raft_pb2

from common.logging import logger

from threading import Condition
import concurrent
from time import time


LEADER_CONDVAR = Condition()

HEARTBEAT_TIMEOUT = 0.2
HEARTBEAT_CYCLE_TIMEOUT = 0.4
BETWEEN_HEARTBEATS = 0.5


def heartbeat_task(grpc_stub):
    try:
        response = grpc_stub.AppendEntries(
            raft_pb2.AppendEntriesRequest(
                term=STATE.term,
                leader_id=MY_ID,
                log_prev_term=STATE.log[-1].term,
                log_prev_index=len(STATE.log) - 1,
                entries=[],
                leader_commit_index=0
            ),
            timeout=HEARTBEAT_TIMEOUT
        )

        if response.term > STATE.term:
            STATE.update_if_stale(response.term)
            STATUS_HOLDER.status = Status.Follower

    except Exception as err:
        logger.debug(f"Something went wrong inside heartbeat task. What: {str(err)}")


def send_heartbeats():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = set()
        for _, grpc_stub in SERVER_MASTER.servers.items():
            futures.add(executor.submit(heartbeat_task(grpc_stub)))

        try:
            for _ in concurrent.futures.as_completed(futures, timeout=HEARTBEAT_CYCLE_TIMEOUT):
                if not STATUS_HOLDER.status != Status.Leader:
                    for unfinished_future in futures:
                        unfinished_future.cancel()
                    break
        except Exception as err:
            logger.error(f"Something went wrong during the heartbeat cycle. What: {str(err)}")


def leader_routine():
    while True:
        with LEADER_CONDVAR:
            while STATUS_HOLDER.status != Status.Leader:
                LEADER_CONDVAR.wait()

        while STATUS_HOLDER.status == Status.Leader:
            timepoint = time()
            send_heartbeats()
            while time() < timepoint + BETWEEN_HEARTBEATS:
                pass
