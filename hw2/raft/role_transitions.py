from raft.state import STATE, LEADER_STATE, LeaderState
from raft.status import STATUS_HOLDER, Status
from raft.config import MY_ID
from raft.leader import LEADER_CONDVAR

from common.logging import logger


def transit_to_follower():
    if STATUS_HOLDER.status == Status.Follower:
        return
    STATUS_HOLDER.status = Status.Follower
    logger.info(f"Server {MY_ID} transited to follower mode in term {STATE.term}")


def transit_to_candidate():
    if STATUS_HOLDER.status == Status.Candidate:
        return
    STATUS_HOLDER.status = Status.Candidate
    logger.info(f"Server {MY_ID} transited to candidate mode in term {STATE.term}")


def transit_to_leader():
    if STATUS_HOLDER.status == Status.Leader:
        return
    LEADER_STATE.reinit(len(STATE.log) - 1)
    with LEADER_CONDVAR:
        STATUS_HOLDER.status = Status.Leader
        STATE.leader_id = MY_ID
        LEADER_CONDVAR.notify()
    logger.info(f"Server {MY_ID} transited to leader mode in term {STATE.term}")
