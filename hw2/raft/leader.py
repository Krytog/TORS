from raft.status import STATUS_HOLDER, Status
from raft.state import STATE, LEADER_STATE
from raft.servers import SERVER_MASTER
from raft.config import MY_ID, CONFIG

from proto import raft_pb2

from common.logging import logger

from threading import Condition
import concurrent
from time import time


LEADER_CONDVAR = Condition()

HEARTBEAT_TIMEOUT = 0.2
HEARTBEAT_CYCLE_TIMEOUT = 0.4
BETWEEN_HEARTBEATS = 0.5


def heartbeat_task(server, grpc_stub):
    try:
        entries = []
        next_index, _ = LEADER_STATE.get_indices_safe(server)
        for i in range(next_index, len(STATE.log)):
            entry = STATE.get_log_entry_safe(i)
            entries.append(
                raft_pb2.LogEntry(
                    term=entry.term,
                    command=entry.command,
                    key=entry.key,
                    value=entry.value,
                )
            )
        entry = STATE.get_log_entry_safe(next_index - 1)
        response = grpc_stub.AppendEntries(
            raft_pb2.AppendEntriesRequest(
                term=STATE.term,
                leader_id=MY_ID,
                log_prev_term=entry.term,
                log_prev_index=next_index - 1,
                entries=entries,
                leader_commit_index=STATE.log_commited_index,
            ),
            timeout=HEARTBEAT_TIMEOUT
        )

        if response.term > STATE.term:
            STATE.update_if_stale(response.term)
            STATUS_HOLDER.status = Status.Follower
            return

        if response.is_successful:
            with LEADER_STATE.mutex:
                LEADER_STATE.log_next_index[server] = len(STATE.log)
                LEADER_STATE.log_match_index[server] = len(STATE.log) - 1
        else:
            with LEADER_STATE.mutex:
                LEADER_STATE.log_next_index[server] -= 1

    except Exception as err:
        logger.debug(f"Something went wrong inside heartbeat task. What: {str(err)}")


def send_heartbeats():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = set()
        for server, grpc_stub in SERVER_MASTER.servers.items():
            futures.add(executor.submit(heartbeat_task(server, grpc_stub)))

        try:
            for _ in concurrent.futures.as_completed(futures, timeout=HEARTBEAT_CYCLE_TIMEOUT):
                if not STATUS_HOLDER.status != Status.Leader:
                    for unfinished_future in futures:
                        unfinished_future.cancel()
                    break
        except Exception as err:
            logger.error(f"Something went wrong during the heartbeat cycle. What: {str(err)}")


def try_commit():
    possible_commit_index = STATE.log_commited_index
    while possible_commit_index < len(STATE.log):
        possible_commit_index += 1
        match_count = 1  # match with ourself
        for _, match_index in LEADER_STATE.log_match_index.items():
            if match_index >= possible_commit_index:
                match_count += 1
        if match_count >= len(CONFIG) // 2 + 1:
            STATE.log_commited_index = possible_commit_index


def leader_routine():
    while True:
        with LEADER_CONDVAR:
            while STATUS_HOLDER.status != Status.Leader:
                LEADER_CONDVAR.wait()

        while STATUS_HOLDER.status == Status.Leader:
            timepoint = time()
            print("I'M LEADER, MY LOG IS:", STATE.log, flush=True)
            send_heartbeats()
            while time() < timepoint + BETWEEN_HEARTBEATS:
                pass
