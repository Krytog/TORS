from raft.state import STATE, LEADER_STATE, LeaderState
from raft.status import STATUS_HOLDER, Status
from raft.config import MY_ID

from common.logging import logger


def transit_to_follower():
    global LEADER_STATE
    LEADER_STATE = None
    STATUS_HOLDER.status = Status.Follower
    logger.info(f"Server {MY_ID} transited to follower mode")


def transit_to_candidate():
    STATUS_HOLDER.status = Status.Candidate
    logger.info(f"Server {MY_ID} transited to candidate mode")


def transit_to_leader():
    global LEADER_STATE
    LEADER_STATE = LeaderState(len(STATE.log))
    logger.info(f"Server {MY_ID} transited to leader mode")
