from enum import Enum

class Status(Enum):
    Follower = 1
    Candidate = 2
    Leader = 3


class StatusHolder:
    def __init__(self):
        self.status = Status.Follower


STATUS_HOLDER = StatusHolder()
